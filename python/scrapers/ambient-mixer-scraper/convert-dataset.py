from typing import Iterable, Optional, Callable
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


def create_system_prompt():
    return r"""Your task is to mix ambient sounds by composing a set of ambient audio tracks.
You can assign each track a <volume> between 0 and 1.
You can only use each track once.
Tracks will loop indefinitely unless <random> is set to true.
In this case, the track will repeat randomly every <random_unit> for <random_counter> times.
Your response should be a JSON object of the following format:
---
[
  {
    "name": "<track name>",
    "volume": "<the volume>",
    "random": "<true or false>",
    "random_counter": "<number of times to play the sound every random_unit if random = true>",
    "random_unit": "<1m|10m|1h>",
  },
  ...
]
---
I will provide descriptions of the enviroment and mood I'd like to create an ambient mix for in my next prompt.
"""


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


def create_message_content_creator(
    min_title_word_count: int,
    min_description_word_count: int,
    remove_digits: bool,
    min_chars: int = 10,
) -> Callable[[MixTrack], Optional[str]]:
    def message_content_creator(mix_track: MixTrack) -> Optional[str]:
        content = ""
        if len(mix_track.title.split()) >= min_title_word_count:
            content += mix_track.title + ": "
        if len(mix_track.description.split()) >= min_description_word_count:
            content += mix_track.description
        if remove_digits:
            # Remove any numbers from content
            content = "".join([x for x in content if not x.isdigit()])
        if len(content) < min_chars:
            return None
        return content

    return message_content_creator


def create_messages(
    mix_track: MixTrack,
    system_prompt: Optional[str],
    user_prompt: str,
) -> list[dict[str, str]]:
    prompts = [{"role": "system", "content": system_prompt}] if system_prompt else []

    return [
        *prompts,
        {"role": "user", "content": user_prompt},
        {
            "role": "assistant",
            "content": json.dumps(
                [
                    {
                        "name": x.name,
                        "volume": x.volume / 100,  # Scale volume to be in [0, 1]
                        "random": x.random,
                        "random_counter": x.random_counter if x.random else 0,
                        "random_unit": x.random_unit if x.random else "1h",
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
    min_title_word_count: int = 2,
    min_description_word_count: int = 5,
    remove_digits: bool = True,
    min_chars: int = 10,
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
        system_prompt = create_system_prompt()
    else:
        system_prompt = None

    user_prompt_generator = create_message_content_creator(
        min_title_word_count=min_title_word_count,
        min_description_word_count=min_description_word_count,
        remove_digits=remove_digits,
        min_chars=min_chars,
    )

    # Create conversational dataset
    conversation = [
        {"messages": create_messages(x, system_prompt, user_prompt)}
        for x in tracks
        if (user_prompt := user_prompt_generator(x))
    ]

    # Remove any messages with content less than min_content_length

    with open(output_path, "w") as output_stream:
        for obj in conversation:
            json.dump(obj, output_stream)
    typer.echo(f"Created conversation with {len(conversation)} prompts.")


if __name__ == "__main__":
    typer.run(convert_dataset)
