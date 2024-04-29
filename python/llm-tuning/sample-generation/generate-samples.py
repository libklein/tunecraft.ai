from typing import Annotated, Iterable
import typer
from pathlib import Path
import json

SOUND_EXTENSIONS = [".mp3", ".wav", ".ogg", ".mp4"]

SYSTEM_PROMPT_TEMPLATE = r"""
Your task is to mix ambient sounds by composing a set of ambient audio tracks.
You can assign each track a <volume> between 0 and 1.
You can only use each track once.
Tracks will loop indefinitely unless <random> is set to true.
In this case, the track will repeat randomly every <random_unit> for <random_counter> times.
You can use the following tracks:
{TRACKS}
Your response should be a JSON object of the following format:
---
[
  {{
    "name": "<track name>",
    "volume": <the volume>,
    "random": <true or false>,
    "random_counter": <number of times to play the sound every random_unit if random = true>,
    "random_unit": "<1m|10m|1h>",
  }},
  ...
]
---
I will provide descriptions of the environment and mood I'd like to create an ambient mix for in my next prompt.
"""


def create_system_prompt(tracks: Iterable[str]) -> str:
    tracks = "\n".join(tracks)
    return SYSTEM_PROMPT_TEMPLATE.format(TRACKS=tracks)


def generate_conversations(
    prompts_file: Annotated[
        Path, typer.Argument(file_okay=True, dir_okay=False, exists=True)
    ],
    sounds_directory: Annotated[
        Path, typer.Argument(dir_okay=True, exists=True, file_okay=False)
    ],
    output_file: Annotated[Path, typer.Option(file_okay=True)] = Path(
        "./conversation.json"
    ),
):
    # Read the prompts file
    prompts = json.load(prompts_file.open())
    sound_files = set().union(
        *[
            set(x.name for x in sounds_directory.rglob(f"*{ext}"))
            for ext in SOUND_EXTENSIONS
        ]
    )

    system_prompt = create_system_prompt(sound_files)

    converstations = []
    for prompt in prompts:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "[noprose]\n[onlyjson]\n" + prompt},
        ]
        converstations.append(messages)

    # Write the conversations to a file
    output_file.write_text(json.dumps(converstations))


if __name__ == "__main__":
    typer.run(generate_conversations)
