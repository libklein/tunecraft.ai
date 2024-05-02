import { drizzle } from 'drizzle-orm/vercel-postgres';
import { createPool } from "@vercel/postgres";
import { POSTGRES_URL } from '$env/static/private';

export const db = drizzle(createPool({ connectionString: POSTGRES_URL }))
