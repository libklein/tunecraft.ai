import { error, json } from '@sveltejs/kit'
import type { RequestHandler } from '../$types'
import { generateAmbientMix } from '$lib/ai.server';
import { audioResources } from '$lib/tracks';
import type { TrackResponseItem } from '$lib/models';
import jsonschema from 'jsonschema';
import TrackResponseSchema from '$lib/TrackResponse.schema.json';
import type { TrackMixAiResponse } from '$lib/models';
import { db } from '$lib/database';
import { PredictionTable, MixesTable, TrackMixTable } from '@/database/schema';

async function insertIntoDatabase(query: string, response: TrackMixAiResponse, tracks: TrackResponseItem[]): Promise<string> {
  // Insert Prediction
  const prediction = (await db.insert(PredictionTable).values({
    provider: response.provider,
    model: response.model,

    requestTimestamp: response.requestTimestamp,
    responseTimestamp: response.responseTimestamp,
    seed: response.seed,

    systemPrompt: response.systemPrompt,
    userPrompt: response.userPrompt,

    modelResponse: response.modelResponse,

    promptTokens: response.promptTokens,
    responseTokens: response.responseTokens,
  }).returning({ id: PredictionTable.id }))[0];

  // Insert Mix
  const mix = (await db.insert(MixesTable).values({
    query: query,
    predictionId: prediction.id
  }).returning({ id: MixesTable.id }))[0];

  // Insert TrackMixes
  await Promise.all(tracks.map(async (track) => {
    await db.insert(TrackMixTable).values({
      mixId: mix.id,
      track: track.name,
      volume: track.volume,
      random: track.random,
      period: track.random_unit,
      frequency: track.random_counter
    });
  }));

  return mix.id;
}

export const POST: RequestHandler = async ({ request }) => {
  const postData = await request.json();
  const query = postData.query;
  // Query AI
  const response = await generateAmbientMix(audioResources.map(elem => elem.name), query);
  const mix: TrackResponseItem[] = response.trackMix;
  // Set defaults
  mix.forEach((track) => {
    track.random = track.random ?? false;
    track.random_unit = track.random_unit ?? "1h";
    track.random_counter = track.random_counter ?? 1;
  });

  // Save to database
  const mixId = await insertIntoDatabase(query, response, mix);

  // Validate schema. 
  const validator = new jsonschema.Validator();
  const validation = validator.validate(mix, TrackResponseSchema);
  if (validation.errors.length > 0) {
    return error(500, 'Invalid response from AI. Please adjust your prompt or try again later.')
  }

  return json({ mixId, mix });
}

