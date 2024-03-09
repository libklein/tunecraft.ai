from typing import Annotated, Optional
import typer
from pathlib import Path
from datasets import load_dataset
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from trl import setup_chat_format
from peft import LoraConfig, AutoPeftModelForCausalLM
from transformers import TrainingArguments
from trl import SFTTrainer
from random import randint
from rich.progress import Progress, track
import json

cli = typer.Typer()

def log_into_huggingface(token: str):
    from huggingface_hub import login
    login(token=token, add_to_git_credential=True)

def process_dataset(dataset_path: Path, output_path: Path):
    # Load dataset
    dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    dataset = dataset.train_test_split(test_size=0.1)

    # Write to disk
    dataset_train_path = output_path / (dataset_path.with_suffix("").name+'-train.json')
    dataset_test_path = output_path / (dataset_path.with_suffix("").name+'-test.json')

    dataset['train'].to_json(str(dataset_train_path), orient="records")
    dataset['test'].to_json(str(dataset_test_path), orient="records")

    # Reload dataset
    return load_dataset("json", data_files=str(dataset_train_path), split="train")

@cli.command()
def finetune(
    model_id: str,
    dataset_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True)],
    output_dir: Annotated[Path, typer.Argument(file_okay=False, dir_okay=True, writable=True)],
    huggingface_token: Optional[str] = None,
    epochs: int = 3,
    learning_rate: float = 2e-4,
    batch_size: int = 32,
    max_seq_length: int = 2048,
    use_attention: Annotated[bool, typer.Option(" /--without-attention")] = True
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

    # BitsAndBytesConfig int-4 config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2" if use_attention else None,
        quantization_config=bnb_config
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.padding_side = 'right'

    model, tokenizer = setup_chat_format(model, tokenizer)

    # LoRA config based on QLoRA paper & Sebastian Raschka experiment
    peft_config = LoraConfig(
            lora_alpha=128,
            lora_dropout=0.05,
            r=256,
            bias="none",
            target_modules="all-linear",
            task_type="CAUSAL_LM",
    )

    args = TrainingArguments(
        output_dir=str(output_dir), # directory to save and repository id
        num_train_epochs=epochs,                     # number of training epochs
        per_device_train_batch_size=3,          # batch size per device during training
        gradient_accumulation_steps=2,          # number of steps before performing a backward/update pass
        gradient_checkpointing=True,            # use gradient checkpointing to save memory
        optim="adamw_torch_fused",              # use fused adamw optimizer
        logging_steps=10,                       # log every 10 steps
        save_strategy="epoch",                  # save checkpoint every epoch
        learning_rate=learning_rate,                     # learning rate, based on QLoRA paper
        bf16=True,                              # use bfloat16 precision
        tf32=True,                              # use tf32 precision
        max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
        warmup_ratio=0.03,                      # warmup ratio based on QLoRA paper
        lr_scheduler_type="constant",           # use constant learning rate scheduler
        push_to_hub=True,                       # push model to hub
        report_to=['tensorboard'],                # report metrics to tensorboard
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=dataset,
        peft_config=peft_config,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        packing=True,
        dataset_kwargs={
            "add_special_tokens": False,  # We template with special tokens
            "append_concat_token": False, # No need to add additional separator token
        }
    )

    typer.echo("Starting fine-tuning...")

    # start training, the model will be automatically saved to the hub and the output directory
    trainer.train()

    # save model
    trainer.save_model()

    # free the memory again
    del model
    del trainer
    torch.cuda.empty_cache()

    typer.echo("Fine-tuning complete")

@cli.command()
def evaluate(dataset_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False, readable=True)],
    model_dir_or_id: Annotated[Path, typer.Argument(file_okay=False, dir_okay=True, readable=True)],
    output_path: Annotated[Path, typer.Argument(file_okay=True, dir_okay=False, writable=True)],
    huggingface_token: Optional[str] = None):

    if huggingface_token:
        try:
            log_into_huggingface(huggingface_token)
        except ImportError:
            typer.echo("Please install the huggingface_hub package to use this feature")
        except Exception as e:
            typer.echo(f"An error occurred logging into huggingface: {e}")
            exit(1)

    model = AutoPeftModelForCausalLM.from_pretrained(
        model_dir_or_id,
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir_or_id)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

    eval_dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    rand_idx = randint(0, len(eval_dataset))

    # Test on sample 
    prompt = pipe.tokenizer.apply_chat_template(eval_dataset[rand_idx]["messages"][:2], tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=False, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)

    typer.echo(f"Query:\n{eval_dataset[rand_idx]['messages'][1]['content']}")
    typer.echo(f"Original Answer:\n{eval_dataset[rand_idx]['messages'][2]['content']}")
    typer.echo(f"Generated Answer:\n{outputs[0]['generated_text'][len(prompt):].strip()}")

    def evaluate(sample):
        prompt = pipe.tokenizer.apply_chat_template(sample["messages"][:2], tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
        return outputs[0]['generated_text'][len(prompt):].strip()
        # return sample["messages"][2]["content"]

    evaluations = []
    for s in track(eval_dataset.shuffle(), description="Evaluating..."):
        evaluations.append(dict(sample=s, response=evaluate(s)))

    with open(output_path, "w") as f:
        json.dump(evaluations, f)

if __name__ == "__main__":
    cli()
