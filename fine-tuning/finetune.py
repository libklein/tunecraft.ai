from typing import Annotated, Optional
import typer
from pathlib import Path
from datasets import load_dataset
import torch
from transformers import TrainingArguments
from trl import SFTTrainer
from random import randint
from rich.progress import track
import json
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template

cli = typer.Typer()


def log_into_huggingface(token: str):
    from huggingface_hub import login

    login(token=token, add_to_git_credential=True)


def process_dataset(dataset_path: Path, tokenizer, output_path: Path, test_size: float):
    # Load dataset
    dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    dataset = dataset.train_test_split(test_size=test_size)

    # Write to disk
    dataset_train_path = output_path / (
        dataset_path.with_suffix("").name + "-train.json"
    )
    dataset_test_path = output_path / (dataset_path.with_suffix("").name + "-test.json")

    dataset["train"].to_json(str(dataset_train_path), orient="records")
    dataset["test"].to_json(str(dataset_test_path), orient="records")

    # Reload dataset
    train_dataset = load_dataset(
        "json", data_files=str(dataset_train_path), split="train"
    )
    # Patch
    tokenizer = get_chat_template(tokenizer, chat_template="chatml", map_eos_token=True)

    def formatting_prompts_func(dataset):
        messages = dataset["messages"]
        texts = [
            tokenizer.apply_chat_template(
                conversation, tokenize=False, add_generation_prompt=False
            )
            for conversation in messages
        ]
        return {
            "text": texts,
        }

    return train_dataset.map(formatting_prompts_func, batched=True)


def create_model(model_id: str | Path, max_seq_length=2048):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    return model, tokenizer


def prepare_model(model):
    # Patch model LORA
    return FastLanguageModel.get_peft_model(
        model,
        r=16,  # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
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
        use_rslora=False,  # We support rank stabilized LoRA
        loftq_config=None,  # And LoftQ
    )


def prepare_tokenizer(tokenizer, chat_format):
    return get_chat_template(tokenizer, chat_template="chatml", map_eos_token=True)


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
    test_size: float = 0.1,
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

    model, tokenizer = create_model(model_id, max_seq_length=max_seq_length)

    model = prepare_model(model)

    # Set up chat format
    tokenizer = prepare_tokenizer(tokenizer, chat_format="chatml")

    # Load dataset
    typer.echo("Loading dataset...")
    dataset = process_dataset(dataset_path, tokenizer, output_dir, test_size=test_size)
    typer.echo(f"Dataset length: {len(dataset)}")

    # Set up trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,  # Can make training 5x faster for short sequences.
        args=TrainingArguments(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=60,
            learning_rate=learning_rate,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            num_train_epochs=epochs,
            lr_scheduler_type="linear",
            output_dir="unsloth_mistral-7b-instruct-v0.2-bnb-4bit_with-system-prompt",
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
    model_dir_or_id: str,
    output_path: Annotated[
        Path, typer.Argument(file_okay=True, dir_okay=False, writable=True)
    ],
    huggingface_token: Optional[str] = None,
    max_seq_length: int = 2048,
    use_gpu: bool = False,
    verbose: bool = False,
):
    from llama_cpp import Llama, CompletionUsage
    from rich.table import Table
    from rich.console import Console
    import time

    console = Console()

    if huggingface_token:
        try:
            log_into_huggingface(huggingface_token)
        except ImportError:
            typer.echo("Please install the huggingface_hub package to use this feature")
        except Exception as e:
            typer.echo(f"An error occurred logging into huggingface: {e}")
            exit(1)

    model_dir_or_id = Path(model_dir_or_id)
    if model_dir_or_id.exists():
        model = Llama(
            model_path=str(model_dir_or_id),
            n_gpu_layers=-1 if use_gpu else 0,
            n_ctx=max_seq_length,
            chat_format="chatml",
            verbose=verbose,
        )
    else:
        model = Llama.from_pretrained(
            repo_id=str(model_dir_or_id),
            n_gpu_layers=-1 if use_gpu else 0,
            n_ctx=max_seq_length,
            chat_format="chatml",
            filename="*.gguf",
            verbose=verbose,
        )

    def evaluate_prompt(messages: list[dict]) -> tuple[str, CompletionUsage]:
        model_response = model.create_chat_completion(messages, max_tokens=2048)

        return model_response["choices"][0]["message"]["content"], model_response[
            "usage"
        ]

    eval_dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    rand_idx = randint(0, len(eval_dataset))

    typer.echo(f"Query:\n{eval_dataset[rand_idx]['messages'][:-1]}")
    typer.echo(f"Original Answer:\n{eval_dataset[rand_idx]['messages'][-1]['content']}")
    typer.echo(
        f"Generated Answer:\n{evaluate_prompt(eval_dataset[rand_idx]['messages'][:-1])[0].strip()}"
    )

    # Track time
    start_time = time.time()
    evaluations = []
    for s in track(eval_dataset.shuffle(), description="Evaluating..."):
        sample = s["messages"]
        response, stats = evaluate_prompt(sample[:-1])
        evaluations.append(dict(sample=sample, response=response, stats=stats))
    evaluation_time = time.time() - start_time
    typer.echo(
        f"Evaluation time: {evaluation_time:.2f} seconds. Per sample: {evaluation_time/len(eval_dataset):.2f} seconds"
    )

    # Summarize stats
    def get_stats(evaluations, attr_name):
        min_prompt_tokens = min(getattr(x["stats"], attr_name) for x in evaluations)
        max_prompt_tokens = max(getattr(x["stats"], attr_name) for x in evaluations)
        avg_prompt_tokens = sum(
            getattr(x["stats"], attr_name) for x in evaluations
        ) / len(evaluations)
        return min_prompt_tokens, max_prompt_tokens, avg_prompt_tokens

    promp_token_stats = get_stats(evaluations, "PROMPT_TOKENS")
    response_token_stats = get_stats(evaluations, "RESPONSE_TOKENS")
    total_token_stats = get_stats(evaluations, "TOTAL_TOKENS")
    # Print as table with columns Min, Max, Avg and rows Prompt, Response, Total
    table = Table(title="Token Stats")
    table.add_column("Token Type", justify="center")
    table.add_column("Min", justify="center")
    table.add_column("Max", justify="center")
    table.add_column("Avg", justify="center")
    table.add_row("Prompt", *(f"{stat:.2f}" for stat in promp_token_stats))
    table.add_row("Response", *(f"{stat:.2f}" for stat in response_token_stats))
    table.add_row("Total", *(f"{stat:.2f}" for stat in total_token_stats))

    console.print(table)

    with open(output_path, "w") as f:
        json.dump(evaluations, f)


if __name__ == "__main__":
    cli()
