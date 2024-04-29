from typing import Annotated
import typer
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from pathlib import Path
from torch import Tensor
import typer
from rich.console import Console
from rich.table import Table
import json


def get_embeddings(model: SentenceTransformer, audio_names: list[str]) -> Tensor:
    
    embeddings = model.encode(audio_names, prompt="Represent the audio mix description for retrieval: ")
    return embeddings

def query_instruction(model: SentenceTransformer, query: str, embeddings: Tensor):
    query_embedding = model.encode(query, prompt="Represent the audio mix title and description for retrieving supporting documents: ")
    similarities = cos_sim(query_embedding, embeddings)
    return similarities[0]

def encode_mix(mix: dict) -> str:
    title = mix["title"]
    description = mix["description"]

    return f'"Mix Title: {title} | Mix Description: {description}"'

def cli(mix_file: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)], model_name: str = "hkunlp/instructor-large") -> None:
    model = SentenceTransformer(model_name)

    with mix_file.open() as f:
        audio_mixes = json.load(f)
        audio_info = [encode_mix(x) for x in audio_mixes]

    embeddings = get_embeddings(model, audio_info)

    query = typer.prompt("Enter the description")
    n_results = typer.prompt("Enter the number of results to show", type=int, default=10)

    similarities = query_instruction(model, "Mix Description: "+query, embeddings)
    # Use argsort to get the indices of the most similar tracks
    most_similar_indices = similarities.argsort(descending=True)

    most_similar_mixes = [audio_mixes[i] for i in most_similar_indices]

    console = Console()
    table = Table(title=f'Most similar audio tracks to "{query}"')
    table.add_column("Title")
    table.add_column("Description")
    table.add_column("Score")

    for i, mix_info in enumerate(most_similar_mixes[:n_results]):
        table.add_row(mix_info['title'], mix_info['description'], f"{similarities[most_similar_indices[i]].item():.2f}")

    console.print(table)


if __name__ == "__main__":
    typer.run(cli)
