<script lang="ts">
	import AudioTrack from '$lib/AudioTrack.svelte';
	import { DEFAULT_TRACK_MAP } from '$lib/tracks';
	import type { GenerateTrackMixResponse, Track } from '$lib/models';
	import _ from 'lodash';

	let masterVolume: number = 1;

	let selectedTracks: Track[] = [];
	let aiPrompt: string =
		'Relaxing music for studying with a fireplace in the background and some train noises.';

	console.log(DEFAULT_TRACK_MAP);

	async function getSoundMix(aiPrompt: string) {
		// Request to backend
		let trackMix: GenerateTrackMixResponse;
		try {
			const response = await fetch('/api/generate', {
				method: 'POST',
				body: JSON.stringify({ query: aiPrompt }),
				headers: {
					'content-type': 'application/json'
				}
			});
			trackMix = await response.json();
		} catch {
			return;
		}

		selectedTracks = trackMix.map((track) => {
			const trackDefinition = DEFAULT_TRACK_MAP.get(track.name);
			if (!trackDefinition) console.error(`Track ${track.name} not found in track map`);
			return {
				...trackDefinition,
				...track,
				volume: track.volume / 100
			};
		});
		console.log(selectedTracks);
	}
</script>

<div class="container flex flex-col mx-auto max-w-3xl items-center justify-center">
	<textarea bind:value={aiPrompt}></textarea>
	<button on:click={() => getSoundMix(aiPrompt)}></button>
	<div class="container max-w-3xl mx-auto">
		<hr />
		Volume:<input type="range" bind:value={masterVolume} min="0" max="1" step="0.01" />
	</div>
	<div class="container max-w-3xl mx-auto">
		{#each selectedTracks as track}
			<AudioTrack
				name={track.name}
				src={track.src}
				bind:volume={track.volume}
				maxVolume={masterVolume}
			></AudioTrack>
		{/each}
	</div>
</div>
