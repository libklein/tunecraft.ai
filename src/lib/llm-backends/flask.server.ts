import type { TrackResponseItem } from '../models';

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackResponseItem[]> {
  const initialPrompt = `
Your task is to mix ambient sounds by composing a set of ambient audio tracks.
You can assign each track a volume between 0 to 1.
Your response should be a JSON object of the following format:
---
[
  {
    "name": "<track name>",
    "volume": "<the volume>"
  },
  ...
]
---
You have the following tracks available:\n\n
---
${tracks.join("\n")}
---
I will provide descriptions of the enviroments and moods I'd like to create an ambient mix for in my next prompt.
`

  const messages = [
    {
      role: 'system',
      content: initialPrompt
    },
    {
      role: 'user',
      content: query
    }
  ]

  try {
    const response = await fetch('http://127.0.0.1:8080/evaluate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: messages }),
    })

    const completion = await response.json()

    if (completion.length == 0) {
      throw "AI did not return a valid response"
    }

    return completion;
  } catch (e) {
    throw e
  }
}
