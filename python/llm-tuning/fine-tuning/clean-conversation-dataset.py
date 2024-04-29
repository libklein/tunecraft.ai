from typing import Annotated
import typer
import json
from pathlib import Path


def parse_dataset(dataset_path: Path):
    dataset = dataset_path.read_text().replace("\n", "")
    decoder = json.JSONDecoder()
    messages = []
    while dataset:
        message, idx = decoder.raw_decode(dataset)
        messages.append(message)
        dataset = dataset[idx:]
    return messages


def save_dataset(dataset: list, output_path: Path):
    with output_path.open("w") as f:
        for message in dataset:
            f.write(json.dumps(message) + "\n")


def clean_dataset(
    dataset_path: Annotated[
        Path, typer.Argument(file_okay=True, dir_okay=False, exists=True, readable=True)
    ],
    output_path: Annotated[
        Path, typer.Argument(file_okay=True, dir_okay=False, writable=True)
    ],
    resume: bool = False,
):
    # Parse the dataset
    dataset = parse_dataset(dataset_path)

    clean_dataset = []
    if resume and output_path.exists():
        checkpoint = parse_dataset(output_path)
        clean_dataset.extend(checkpoint)

        index = dataset.index(clean_dataset[-1])

        # Remove any messages from the dataset that are already in the clean_dataset
        dataset = dataset[index:]

    typer.echo(
        f"Loaded {len(dataset)} conversations. Checkpoint has {len(clean_dataset)}"
    )

    for i, message in enumerate(dataset):
        typer.echo(f"{i+1}/{len(dataset)}: " + message["messages"][0]["content"])
        # Ask the user if they want to keep the conversation
        keep = typer.confirm("Do you want to keep this conversation?", default=True)
        if keep:
            clean_dataset.append(message)

        # Save the cleaned dataset
        save_dataset(clean_dataset, output_path)


if __name__ == "__main__":
    typer.run(clean_dataset)
