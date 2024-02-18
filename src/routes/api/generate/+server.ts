import { error, json } from '@sveltejs/kit'
import type { RequestHandler } from '../$types'
import { generateAmbientMix } from '$lib/ai.server';
import { audioResources } from '$lib/tracks';
import type { TrackResponseItem } from '$lib/models';

export async function POST({ request }: RequestHandler) {
  const postData = await request.json();
  const query = postData.query;
  // Query AI
  const volumeMap: TrackResponseItem[] = await generateAmbientMix(
    audioResources.map(elem => elem.name),
    query
  );

  return json(volumeMap);
}

