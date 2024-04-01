import type { TrackResponseItem } from '../models';

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackResponseItem[]> {
  // Wait 5 seconds
  await new Promise(resolve => setTimeout(resolve, 5000));
  return [
    {
      "name": "Breakwater",
      "volume": 100,
      "random": false,
      "random_counter": 1,
      "random_unit": "1h"
    },
    {
      "name": "Wooden Ship",
      "volume": 90,
      "random": false,
      "random_counter": 5,
      "random_unit": "1h"
    },
    {
      "name": "Ropes",
      "volume": 80,
      "random": true,
      "random_counter": 5,
      "random_unit": "10m"
    },
    {
      "name": "seagull on beach",
      "volume": 63,
      "random": true,
      "random_counter": 3,
      "random_unit": "10m"
    },
    {
      "name": "Flapping Cotton",
      "volume": 63,
      "random": true,
      "random_counter": 5,
      "random_unit": "10m"
    },
    {
      "name": "All I Ask of You Humming",
      "volume": 0,
      "random": false,
      "random_counter": 3,
      "random_unit": "10m"
    },
  ];
}
