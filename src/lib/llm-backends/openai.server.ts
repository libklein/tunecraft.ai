
import OpenAI from 'openai'
import type { TrackMixAiResponse, TrackResponseItem } from '../models'
import { OPENAI_API_KEY, OPENAI_MODEL } from '$env/static/private'
const SystemPromptTemplate = (await import('$lib/SystemPromptTemplate.txt?raw')).default

function extractTrackMix(aiResponse: string): TrackResponseItem[] {
  return JSON.parse(aiResponse)
}

function createSystemPrompt(tracks: string[]): string {
  return SystemPromptTemplate.replace("{TRACKS}", tracks.join("\n"))
}

function createQueryPrompt(query: string): string {
  return "[noprose]\n[onlyjson]\n" + query
}

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackMixAiResponse> {
  const client = new OpenAI({
    apiKey: OPENAI_API_KEY
  })

  const systemPrompt = createSystemPrompt(tracks);
  const userPrompt = createQueryPrompt(query);

  const requestTimestamp = new Date()

  const completion = await client.chat.completions.create({
    model: OPENAI_MODEL,
    seed: 0,
    messages: [{
      role: 'system',
      content: systemPrompt
    },
    {
      role: 'user',
      content: userPrompt
    }],
    stream: false,
  })

  const responseTimestamp = new Date()

  if (completion.choices.length == 0 || !completion.choices[0].message.content) {
    throw "AI did not return a response"
  }

  try {
    // Parse response
    return {
      requestTimestamp: new Date(requestTimestamp.toISOString()),
      responseTimestamp: new Date(responseTimestamp.toISOString()),
      provider: "openai",
      model: OPENAI_MODEL,
      seed: 0,
      systemPrompt: systemPrompt,
      userPrompt: userPrompt,
      modelResponse: completion.choices[0].message.content,

      promptTokens: completion.usage?.prompt_tokens ?? 0,
      responseTokens: completion.usage?.completion_tokens ?? 0,

      trackMix: extractTrackMix(completion.choices[0].message.content)
    }
  } catch {
    throw "Faild to parse AI response"
  }
}
