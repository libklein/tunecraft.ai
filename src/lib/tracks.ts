import type { Track } from "./models";

export const audioResources: Track[] = [
  {
    name: 'glue-birds.mp4',
    src: '/audio/glue-birds.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-crickets.mp4',
    src: '/audio/glue-crickets.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-fire.mp4',
    src: '/audio/glue-fire.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-people.mp4',
    src: '/audio/glue-people.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-sbowl.mp4',
    src: '/audio/glue-sbowl.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-waves.mp4',
    src: '/audio/glue-waves.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'glue-wind.mp4',
    src: '/audio/glue-wind.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-birds.mp4',
    src: '/audio/main-birds.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-crickets.mp4',
    src: '/audio/main-crickets.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-fire.mp4',
    src: '/audio/main-fire.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-people.mp4',
    src: '/audio/main-people.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-sbowl.mp4',
    src: '/audio/main-sbowl.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-thunder.mp4',
    src: '/audio/main-thunder.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-waves.mp4',
    src: '/audio/main-waves.mp4',
    description: '',
    volume: 0
  },
  {
    name: 'main-wind.mp4',
    src: '/audio/main-wind.mp4',
    description: '',
    volume: 0
  }
];


export const DEFAULT_TRACK_MAP: Map<string, Track> = new Map(
  audioResources.map((resource) => [resource.name, resource])
);
