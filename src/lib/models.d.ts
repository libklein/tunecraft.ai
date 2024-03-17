const ONE_MINUTE = "1m";
const TEN_MINUTES = "10m";
const ONE_HOUR = "1h";

export const TRACK_PERIOD_DURATION_TO_SECONDS = {
  [ONE_MINUTE]: 60,
  [TEN_MINUTES]: 600,
  [ONE_HOUR]: 3600
}

export interface Track {
  name: string,
  description: string,
  src: string,
  volume: number,
  random: boolean,
  periodDurationSeconds: ONE_MINUTE | TEN_MINUTES | ONE_HOUR,
  expectedPlaysPerSecond: number
}

interface TrackResponseItem {
  name: string,
  volume: number,
  random: boolean,
  random_unit: ONE_MINUTE | TEN_MINUTES | ONE_HOUR,
  random_counter: number
}

export type GenerateTrackMixResponse = TrackResponseItem[]
