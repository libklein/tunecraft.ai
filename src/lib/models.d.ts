export interface Track {
  name: string,
  description: string,
  src: string,
  volume: number
}

interface TrackResponseItem {
  name: string,
  volume: number
}

export type GenerateTrackMixResponse = TrackResponseItem[]
