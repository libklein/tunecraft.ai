from typing import Annotated, AsyncGenerator, Iterable
import typer
import httpx
from dataclasses import dataclass
import asyncio
from pathlib import Path
from json import load, dump
from rich.progress import track as track_progress

@dataclass
class Track:
    name: str
    src: str
    volume: int = 0

@dataclass
class ScrapedTrack:
    id_audio: str
    name_audio: str
    url_audio: str

async def download_file(client: httpx.AsyncClient, output_path: Path, src: str):
    global semaphore
    async with semaphore:
        reponse = await client.get(src, timeout=10.0)
    reponse.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(reponse.content)


async def download_track(client: httpx.AsyncClient, output_dir: Path, web_root: str, scraped_track: ScrapedTrack) -> tuple[ScrapedTrack, Track | None]:
    output_path = output_dir / f"{scraped_track.id_audio}.mp3"
    web_path = web_root + scraped_track.id_audio + ".mp3"
    try:
        await download_file(client, output_path, scraped_track.url_audio)
    except (httpx.HTTPStatusError, TypeError) as e:
        return scraped_track, None
    return scraped_track, Track(
        name=scraped_track.name_audio,
        src=web_path,
    )

def parse_tracks_file(tracks_file: Path) -> list[ScrapedTrack]:
    tracks = []
    with open(tracks_file, "r") as f:
        tracks_json = load(f)

    for track in tracks_json:
        tracks.append(ScrapedTrack(
            id_audio=track["id_audio"],
            name_audio=track["name_audio"],
            url_audio=track["url_audio"],
        ))
    return tracks

async def run_cli(concurrent_requests: int, tracks_file: Path, output_dir: Path, web_root: str):
    # Create the output directory if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read the tracks
    scraped_tracks = parse_tracks_file(tracks_file)
    # Download the tracks. Show progress as rich progress
    async with httpx.AsyncClient() as client:
        global semaphore
        semaphore = asyncio.Semaphore(concurrent_requests)
        tracks = []
        tasks = [download_track(client, output_dir, web_root, scraped_track) for scraped_track in scraped_tracks]
        for track in track_progress(asyncio.as_completed(tasks), description="Downloading tracks...", total=len(scraped_tracks)):
            scraped_track, resolved_track = await track
            if resolved_track is not None:
                tracks.append(resolved_track)
            else:
                typer.echo(f"Failed to download {scraped_track.name_audio} (ID: {scraped_track.id_audio})", err=True)

    # Serialize the tracks to a file
    with open(output_dir / "tracks.json", "w") as f:
        dump([track.__dict__ for track in tracks], f)

def cli(tracks: Annotated[Path, typer.Argument(dir_okay=False, exists=True)], 
        output_dir: Annotated[Path, typer.Argument(dir_okay=True, file_okay=False)],
        web_root: str,
        concurrent_requests: int = 10):
        asyncio.run(run_cli(concurrent_requests, tracks, output_dir, web_root))

if __name__ == "__main__":
    typer.run(cli)
