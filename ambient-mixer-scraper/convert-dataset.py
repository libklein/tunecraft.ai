from typing import Iterable, Optional
import typer
from pathlib import Path
from dataclasses import dataclass
import json
from collections import Counter


@dataclass(frozen=True)
class Track:
    id: int
    name: str
    url: str
    mute: bool
    volume: int
    balance: int
    random: bool
    random_counter: int
    random_unit: str
    crossfade: bool


@dataclass(frozen=True)
class MixTrack:
    title: str
    description: str
    categories: list[str]
    mix: list[Track]


def create_system_prompt(track_names: Iterable[str]):
    return (
        r"""Your task is to mix ambient sounds by composing a set of ambient audio tracks.
You can assign each track a volume between 0 to 1.
Your response should be a JSON object of the following format:
---
[
  {
    "name": "<track name>",
    "volume": "<the volume>",
    "random": "<true or false>",
    "random_counter": "<how often per minute the sound should play>",
  },
  ...
]
---
You have the following tracks available:\n\n
---"""
        + "\n".join(x for x in track_names)
        + r"""---
I will provide descriptions of the enviroment and mood I'd like to create an ambient mix for in my next prompt.
"""
    )


def parse_track(track: dict) -> Track:
    return Track(
        id=track["id_audio"],
        name=track["name_audio"],
        url=track["url_audio"],
        mute=track["mute"] == "true",
        volume=int(track["volume"]),
        balance=int(track["balance"]),
        random=track["random"] == "true",
        random_counter=int(track["random_counter"]),
        random_unit=track["random_unit"],
        crossfade=track["crossfade"] == "true",
    )


def parse_mix_track(mix_track: dict) -> MixTrack:
    return MixTrack(
        title=mix_track["title"],
        description=mix_track["description"],
        categories=mix_track["categories"],
        mix=[
            parse_track(x) for x in mix_track["mix"].values() if x["name_audio"] != "-"
        ],
    )


def create_messages(
    mix_track: MixTrack, system_prompt: Optional[str]
) -> list[dict[str, str]]:
    prompts = [{"role": "system", "content": system_prompt}] if system_prompt else []
    return [
        *prompts,
        {"role": "user", "content": mix_track.description},
        {
            "role": "assistant",
            "content": json.dumps(
                [
                    {
                        "name": x.name,
                        "volume": x.volume,
                        "random": x.random,
                        "random_counter": x.random_counter if x.random else 0,
                    }
                    for x in mix_track.mix
                ]
            ),
        },
    ]


def get_tracks(mixed_tracks: list[MixTrack], max_tracks: int) -> list[MixTrack]:
    # Find most common tracks
    track_counter = Counter([x.name for y in mixed_tracks for x in y.mix])
    top_tracks = {x[0] for x in track_counter.most_common(max_tracks)}
    # Filter out any mix where at least one track is not in the top tracks
    return [x for x in mixed_tracks if all(y.name in top_tracks for y in x.mix)]


def convert_dataset(
    mixes: Path,
    output_path: Path,
    add_system_prompt: bool = True,
    max_tracks: int = 250,
):
    typer.echo("Converting dataset...")
    # Parse mixes form mixes file, which contains a list of mix tracks in JSON format
    with open(mixes, "r") as f:
        mix_tracks = json.load(f)

    mix_tracks = [parse_mix_track(x) for x in mix_tracks]

    tracks = get_tracks(mix_tracks, max_tracks)

    track_names = {y.name for x in tracks for y in x.mix}
    assert "-" not in track_names

    # Create system prompt
    if add_system_prompt:
        system_prompt = create_system_prompt(track_names)
    else:
        system_prompt = None

    # Create conversational dataset
    conversation = [{"messages": create_messages(x, system_prompt)} for x in tracks]

    with open(output_path, "w") as output_stream:
        for obj in conversation:
            json.dump(obj, output_stream)
    typer.echo(f"Created conversation with {len(conversation)} prompts.")


if __name__ == "__main__":
    typer.run(convert_dataset)
