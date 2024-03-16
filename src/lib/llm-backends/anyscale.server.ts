import OpenAI from 'openai'
import type { TrackResponseItem } from '../models'
import { OPENAI_API_KEY } from '$env/static/private'

const TRACK_MIX_RESPONSE_RE = /[^]*(?<trackMix>\[[^]*\])[^]*/m

function extractTrackMix(aiResponse: string): TrackResponseItem[] {
  const match = aiResponse.match(TRACK_MIX_RESPONSE_RE)
  if (match && Object.hasOwn(match?.groups ?? {}, 'trackMix')) {
    return JSON.parse(match?.groups['trackMix'] as string)
  } else {
    throw "Failed to extract track mix from response"
  }
}

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackResponseItem[]> {
  const client = new OpenAI({
    baseURL: 'https://api.endpoints.anyscale.com/v1',
    apiKey: OPENAI_API_KEY
  })

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

  // Obsolete code, ignore
  const completion = await client.chat.completions.create({
    model: 'meta-llama/Llama-2-70b-chat-hf',
    messages: [{
      role: 'system',
      content: initialPrompt
    },
    {
      role: 'user',
      content: query
    }]
  })

  if (completion.choices.length == 0 || !completion.choices[0].message.content) {
    throw "AI did not return a response"
  }

  try {
    // Parse response
    return extractTrackMix(completion.choices[0].message.content);
  } catch {
    throw ""
  }
}
