
import OpenAI from 'openai'
import type { TrackResponseItem } from '../models'
import { OPENAI_API_KEY } from '$env/static/private'
const SystemPromptTemplate = (await import('$lib/SystemPromptTemplate.txt?raw')).default

const TRACK_MIX_RESPONSE_RE = /[^]*(?<trackMix>\[[^]*\])[^]*/m

function extractTrackMix(aiResponse: string): TrackResponseItem[] {
  return JSON.parse(aiResponse)
  const match = aiResponse.match(TRACK_MIX_RESPONSE_RE)
  if (match && Object.hasOwn(match?.groups ?? {}, 'trackMix')) {
    return JSON.parse(match?.groups['trackMix'] as string)
  } else {
    throw "Failed to extract track mix from response"
  }
}

function createSystemPrompt(tracks: string[]): string {
  return SystemPromptTemplate.replace("{TRACKS}", tracks.join("\n"))
}

function createQueryPrompt(query: string): string {
  return "[noprose]\n[onlyjson]\n" + query
}

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackResponseItem[]> {
  const client = new OpenAI({
    apiKey: OPENAI_API_KEY
  })

  const initialPrompt = createSystemPrompt(tracks);

  const messages = [{
    role: 'system',
    content: initialPrompt
  },
  {
    role: 'user',
    content: createQueryPrompt(query)
  }]

  const completion = await client.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{
      role: 'system',
      content: initialPrompt
    },
    {
      role: 'user',
      content: createQueryPrompt(query)
    }],
    stream: false,
  })

  if (completion.choices.length == 0 || !completion.choices[0].message.content) {
    throw "AI did not return a response"
  }

  try {
    // Parse response
    return extractTrackMix(completion.choices[0].message.content);
  } catch {
    throw "Faild to parse AI response"
  }
}
