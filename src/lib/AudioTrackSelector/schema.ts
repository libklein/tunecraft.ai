import { z } from "zod";

export const formSchema = z.object({
  name: z.string().default('new Track'),
  description: z.string(),
  src: z.string().url(),
  volume: z.number().default(0),
  random: z.boolean().default(false),
  periodDurationSeconds: z.union([
    z.literal("1m"),
    z.literal("10m"),
    z.literal("1h")
  ]).default("1m"),
  expectedPlaysPerPeriod: z.number().min(0).default(0)
});

export type FormSchema = typeof formSchema;
