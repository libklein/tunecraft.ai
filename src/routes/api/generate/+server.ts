import { error, json } from '@sveltejs/kit'
import type { RequestHandler } from '../$types'
import { generateAmbientMix } from '$lib/ai.server';
import { audioResources } from '$lib/tracks';
import type { TrackResponseItem } from '$lib/models';
import jsonschema from 'jsonschema';
import TrackResponseSchema from '$lib/TrackResponse.schema.json';

export const POST: RequestHandler = async ({ request }) => {
  const postData = await request.json();
  const query = postData.query;
  // Query AI
  const volumeMap: TrackResponseItem[] = await generateAmbientMix(
    audioResources.map(elem => elem.name),
    query
  );

  // Validate schema. 
  const validator = new jsonschema.Validator();
  const validation = validator.validate(volumeMap, TrackResponseSchema);
  if (validation.errors.length > 0) {
    return error(500, 'Invalid response from AI. Please adjust your prompt or try again later.')
  }

  return json(volumeMap);
}

