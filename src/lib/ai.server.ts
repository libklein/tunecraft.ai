import OpenAI from 'openai'
import type { Track } from './models'
import { OPENAI_API_KEY } from '$env/static/private'

console.log(OPENAI_API_KEY)

const TRACK_MIX_RESPONSE_RE = /[^]*(?<trackMix>\[[^]*\])[^]*/m

function extractTrackMix(aiResponse: string): AITrackResponseItem[] {
  const match = aiResponse.match(TRACK_MIX_RESPONSE_RE)
  console.log(match)
  if (match && Object.hasOwn(match?.groups ?? {}, 'trackMix')) {
    return JSON.parse(match?.groups['trackMix'] as string)
  } else {
    throw "Failed to extract track mix from response"
  }
}

export async function generateAmbientMix(tracks: string[], query: string): Promise<AITrackResponseItem[]> {
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

  console.log(initialPrompt)

  const completion = await client.chat.completions.create({
    model: 'meta-llama/Llama-2-70b-chat-hf',
    messages: [{
      role: 'system',
      content: initialPrompt
    },
    {
      role: 'user',
      content: query
    }],
    // response_format: {
    //   type: 'json_object',
    //   schema:
    //   {
    //     "$schema": "http://json-schema.org/draft-04/schema#",
    //     "type": "array",
    //     "items":
    //     {
    //       "type": "object",
    //       "properties": {
    //         "name": {
    //           "type": "string"
    //         },
    //         "volume": {
    //           "type": "string"
    //         }
    //       },
    //       "required": [
    //         "name",
    //         "volume"
    //       ]
    //     }
    //
    //   }
    // }
  })


  if (completion.choices.length == 0 || !completion.choices[0].message.content) {
    throw "AI did not return a response"
  }

  console.log(completion.choices[0].message.content);

  try {
    // Parse response
    return extractTrackMix(completion.choices[0].message.content);
  } catch {
    throw ""
  }

}
