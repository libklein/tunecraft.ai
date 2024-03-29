import type { Track } from "./models";
import tracks from "./tracks.json";

export const audioResources: Track[] = tracks.map(track => ({
  ...track,
  description: "",
  random: false,
  periodDurationSeconds: 10,
  expectedPlaysPerPeriod: 1
}))

export const DEFAULT_TRACK_MAP: Map<string, Track> = new Map(
  audioResources.map((resource) => [resource.name, resource])
);
