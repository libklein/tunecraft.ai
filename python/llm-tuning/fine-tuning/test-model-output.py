import typer
from pathlib import Path
from typing import Annotated
import json
import math
import random
import pydub
import pydub.playback as playback
from pprint import pprint as print

def play_track_mix(tracks: dict[str, Path], mix: dict):
    audio = []
    for track in mix:
        track_name = track["name"]
        track_volume = track["volume"]

        if track_name == '-':
            continue
        if track_name not in tracks:
            typer.echo(f"Track {track_name} not found", err=True)
            continue
        if track_volume < 0 or track_volume > 100:
            typer.echo(f"Invalid volume for track {track_name}: {track_volume}", err=True)
            continue
        if track_volume == 0:
            continue

        track_file = tracks[track_name]
        pb = pydub.AudioSegment.from_file(track_file)
        # Set pb volume to track_volume
        pb = pb + math.log10(track_volume/100)
        audio.append(pb)
    audio.sort(key=lambda x: x.duration_seconds, reverse=True)
    res = audio[0]
    for pb in audio[1:]:
        res = res.overlay(pb, loop=True)
    return res

def play_random_mix(model_output: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)], audio_dir: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)], track_file: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)], playback_duration: int = 10):
    with open(model_output, "r") as f:
        parsed_model_output = json.load(f)
    with open(track_file, "r") as f:
        tracks = {track["name"]: audio_dir/(track["src"].split("/")[-1]) for track in json.load(f)}

    # Select a random item
    sample = random.choice(parsed_model_output)

    typer.echo(sample["sample"]['messages'][1]['content'])

    label_mix = json.loads(sample["sample"]['messages'][-1]['content'])
    response_mix = json.loads(sample["response"])

    label_audio = play_track_mix(tracks, label_mix)
    label_audio = label_audio[:playback_duration*1000]
    # Play label audio
    typer.echo(f"Playing label audio ({label_audio.max_dBFS} db, {label_audio.duration_seconds}) seconds")
    print(label_mix)
    playback.play(label_audio)

    response_audio = play_track_mix(tracks, response_mix)
    response_audio = response_audio[:playback_duration*1000]
    # Play response audio
    typer.echo(f"Playing response audio ({response_audio.max_dBFS} db, {response_audio.duration_seconds}) seconds")
    print(response_mix)
    playback.play(response_audio)



if __name__ == "__main__":
    typer.run(play_random_mix)
