import type { TrackMixAiResponse, TrackResponseItem } from '../models';

export async function generateAmbientMix(tracks: string[], query: string): Promise<TrackMixAiResponse> {
  // Wait 5 seconds
  await new Promise(resolve => setTimeout(resolve, 5000));
  const trackMix: TrackResponseItem[] = [
    {
      "name": "Birdsong",
      "volume": 0,
      "random": false,
      "random_counter": 3,
      "random_unit": "10m"
    },
    {
      "name": "Burning campfire",
      "volume": 0,
      "random": false,
      "random_counter": 3,
      "random_unit": "10m"
    }
  ];

  return {
    requestTimestamp: new Date(),
    responseTimestamp: new Date(),
    provider: "mock",
    model: "mock",
    seed: 0,
    systemPrompt: "",
    userPrompt: "",
    modelResponse: "",
    promptTokens: 0,
    responseTokens: 0,
    trackMix

  }
}
