import json
from pathlib import Path

PROMPT_TEMPLATE = r"""
[noprompt]
[onlyjson]
I have a list of descriptions of audio files. I'd like you to remove descriptions that are not proper English. Please output only the descriptions you have decided to keep. Please format your response as a JSON list of strings. I'll provide the descriptions now:
---
{DESCRIPTIONS}
"""

mixes = json.load(Path("mixes.json").open())

descriptions = [x["description"] for x in mixes]

next_index = 0
while next_index < len(descriptions):
    descriptions_chunk = descriptions[next_index : next_index + 150]
    prompt = PROMPT_TEMPLATE.format(
        DESCRIPTIONS="\n".join(map(lambda x: f'"{x}"', descriptions_chunk))
    )
    Path(f"prompts/{next_index}.txt").write_text(prompt)
    next_index += 150
