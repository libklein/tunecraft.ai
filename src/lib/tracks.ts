import type { Track } from "./models";
import tracks from "./tracks.json";

export const audioResources: Track[] = tracks.map(track => ({
  ...track,
  description: "",
  random: false,
  randomUnit: "1m",
  randomFrequency: 0
}))

export const DEFAULT_TRACK_MAP: Map<string, Track> = new Map(
  audioResources.map((resource) => [resource.name, resource])
);
