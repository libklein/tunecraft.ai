
import { error, json } from '@sveltejs/kit'
import type { RequestHandler } from '../$types'
import { db } from '$lib/database';
import { RatingTable } from '@/database/schema';

export const POST: RequestHandler = async ({ request }) => {
  const postData = await request.json();
  const rating = postData.rating;
  const mixId = postData.mixId;

  // Error if rating is not a number between -1 and 1
  if (typeof rating !== 'number' || rating < -1 || rating > 1) {
    return error(400);
  }
  if (typeof mixId !== 'string') {
    return error(400);
  }

  // Insert into database
  try {
    const [dbRating] = await db.insert(RatingTable).values({
      mixId: mixId,
      rating: rating,
    }).returning({ mixId: RatingTable.mixId, id: RatingTable.id });
    return json(dbRating);
  } catch (e) {
    return error(400);
  }
}

