import {
  pgTable as table,
  uuid,
  integer,
  varchar,
  text,
  timestamp,
  interval,
  boolean,
  real,
} from 'drizzle-orm/pg-core'

import type { AnyPgColumn } from 'drizzle-orm/pg-core';


export const PredictionTable = table('predictions', {
  id: uuid('id').defaultRandom().primaryKey(),
  // Metadata
  timestamp: timestamp('timestamp').defaultNow(),
  provider: text('provider').notNull(),
  model: text('model').notNull(),
  duration: interval('duration').notNull(),
  seed: integer('seed'),

  // Model input
  systemPrompt: text('systemPrompt').notNull(),
  userPrompt: text('userPrompt').notNull(),
  // Model output
  modelResponse: text('modelResponse').notNull(),

  // Usage
  promptTokens: integer('promptTokens').notNull(),
  responseTokens: integer('responseTokens').notNull(),
});


export const MixesTable = table('mixes', {
  id: uuid('id').defaultRandom().primaryKey(),
  query: text('query').notNull(),
  // Metadata
  timestamp: timestamp('timestamp').defaultNow(),
  predictionId: uuid('predictionId').references(() => PredictionTable.id),
});

export const TrackMixTable = table('trackMixes', {
  id: uuid('id').defaultRandom().primaryKey(),
  mixId: uuid('mixId').references(() => MixesTable.id),
  // Tracks
  track: varchar('track', { length: 256 }).notNull(),
  volume: real('volume').notNull(),
  random: boolean('random').notNull(),
  period: varchar('period', { length: 32 }).notNull(),
  frequency: integer('frequency').notNull(),
});

export const RatingTable = table('ratings', {
  id: uuid('id').defaultRandom().primaryKey(),
  mixId: uuid('mixId').references(() => MixesTable.id),
  rating: integer('rating').notNull(),
  comment: text('comment'),
  timestamp: timestamp('timestamp').defaultNow(),
});
