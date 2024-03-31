from typing import Annotated, Optional
import typer
from pathlib import Path
from datasets import load_dataset
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline,
)
from trl import setup_chat_format
from peft import LoraConfig, AutoPeftModelForCausalLM
from transformers import TrainingArguments
from trl import SFTTrainer
from random import randint
from rich.progress import Progress, track
import json
from unsloth import FastLanguageModel

cli = typer.Typer()


def log_into_huggingface(token: str):
    from huggingface_hub import login

    login(token=token, add_to_git_credential=True)


def process_dataset(dataset_path: Path, output_path: Path):
    # Load dataset
    dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    dataset = dataset.train_test_split(test_size=0.1)

    # Write to disk
    dataset_train_path = output_path / (
        dataset_path.with_suffix("").name + "-train.json"
    )
    dataset_test_path = output_path / (dataset_path.with_suffix("").name + "-test.json")

    dataset["train"].to_json(str(dataset_train_path), orient="records")
    dataset["test"].to_json(str(dataset_test_path), orient="records")

    # Reload dataset
    return load_dataset("json", data_files=str(dataset_train_path), split="train")


def create_model(model_id: str | Path, max_seq_length=2048):
    # Load Llama model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.padding_side = "right"
    return model, tokenizer


@cli.command()
def finetune(
    model_id: str,
    dataset_path: Annotated[
        Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True)
    ],
    output_dir: Annotated[
        Path, typer.Argument(file_okay=False, dir_okay=True, writable=True)
    ],
    huggingface_token: Optional[str] = None,
    epochs: int = 3,
    learning_rate: float = 2e-4,
    batch_size: int = 8,
    max_seq_length: int = 2048,
):
    typer.echo(f"Fine-tuning {model_id} on {dataset_path} for {epochs} epochs")
    typer.echo(f"Learning rate: {learning_rate}, Batch size: {batch_size}")

    if huggingface_token:
        try:
            log_into_huggingface(huggingface_token)
        except ImportError:
            typer.echo("Please install the huggingface_hub package to use this feature")
        except Exception as e:
            typer.echo(f"An error occurred logging into huggingface: {e}")
            exit(1)

    typer.echo("Loading dataset...")

    dataset = process_dataset(dataset_path, output_dir)
    print("Dataset length:",len(dataset))

    model, tokenizer = create_model(model_id, max_seq_length=max_seq_length)
    model, tokenizer = setup_chat_format(model, tokenizer)

    # Do model patching and add fast LoRA weights
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,  # Supports any, but = 0 is optimized
        bias="none",  # Supports any, but = "none" is optimized
        use_gradient_checkpointing=True,
        random_state=3407,
        max_seq_length=max_seq_length,
        use_rslora=False,  # We support rank stabilized LoRA
        loftq_config=None,  # And LoftQ
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=TrainingArguments(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=60,
            learning_rate=learning_rate,
            num_train_epochs=epochs,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            output_dir=str(output_dir),
            optim="adamw_8bit",
            seed=3407,
            push_to_hub=True,
            report_to=["tensorboard"],
        ),
    )

    typer.echo("Starting fine-tuning...")

    # start training, the model will be automatically saved to the hub and the output directory
    trainer.train()

    # save model
    trainer.save_model()

    typer.echo("Fine-tuning complete")

    typer.echo("Saving quantized model...")

    model.push_to_hub_gguf(
        f"libklein/{output_dir.name}-q4_k_m", tokenizer, quantization_method="q4_k_m"
    )
    model.push_to_hub_gguf(
        f"libklein/{output_dir.name}-q8_0", tokenizer, quantization_method="q8_0"
    )
    model.push_to_hub_gguf(
        f"libklein/{output_dir.name}-quantized",
        tokenizer,
        quantization_method="quantized",
    )

    typer.echo("Model saved to hub")

    # free the memory again
    del model
    del trainer
    torch.cuda.empty_cache()


@cli.command()
def evaluate(
    dataset_path: Annotated[
        Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True)
    ],
    model_dir_or_id: Annotated[
        Path, typer.Argument(file_okay=False, dir_okay=True, readable=True)
    ],
    output_path: Annotated[
        Path, typer.Argument(file_okay=True, dir_okay=False, writable=True)
    ],
    huggingface_token: Optional[str] = None,
):
    if huggingface_token:
        try:
            log_into_huggingface(huggingface_token)
        except ImportError:
            typer.echo("Please install the huggingface_hub package to use this feature")
        except Exception as e:
            typer.echo(f"An error occurred logging into huggingface: {e}")
            exit(1)

    model, tokenizer = create_model(model_dir_or_id, use_attention=False)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

    eval_dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    rand_idx = randint(0, len(eval_dataset))

    # Test on sample
    prompt = pipe.tokenizer.apply_chat_template(
        eval_dataset[rand_idx]["messages"][:2],
        tokenize=False,
        add_generation_prompt=True,
    )
    outputs = pipe(
        prompt,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.1,
        top_k=50,
        top_p=0.1,
        eos_token_id=pipe.tokenizer.eos_token_id,
        pad_token_id=pipe.tokenizer.pad_token_id,
    )

    typer.echo(f"Query:\n{eval_dataset[rand_idx]['messages'][1]['content']}")
    typer.echo(f"Original Answer:\n{eval_dataset[rand_idx]['messages'][2]['content']}")
    typer.echo(
        f"Generated Answer:\n{outputs[0]['generated_text'][len(prompt):].strip()}"
    )

    def evaluate(sample):
        prompt = pipe.tokenizer.apply_chat_template(
            sample["messages"][:2], tokenize=False, add_generation_prompt=True
        )
        outputs = pipe(
            prompt,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            eos_token_id=pipe.tokenizer.eos_token_id,
            pad_token_id=pipe.tokenizer.pad_token_id,
        )
        return outputs[0]["generated_text"][len(prompt) :].strip()
        # return sample["messages"][2]["content"]

    evaluations = []
    for s in track(eval_dataset.shuffle(), description="Evaluating..."):
        evaluations.append(dict(sample=s, response=evaluate(s)))

    with open(output_path, "w") as f:
        json.dump(evaluations, f)


if __name__ == "__main__":
    cli()
