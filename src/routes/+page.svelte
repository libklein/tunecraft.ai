<script lang="ts">
	import AudioTrack from '$lib/AudioTrack.svelte';
	import { DEFAULT_TRACK_MAP } from '$lib/tracks';
	import type { GenerateTrackMixResponse, Track } from '$lib/models';
	import _ from 'lodash';

	let masterVolume: number = 1;

	let audioTracks: Map<string, Track> = DEFAULT_TRACK_MAP;
	let aiPrompt: string;

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

		// TODO Handle failure

		// Update the audio track volumes
		trackMix.forEach(({ name, volume }) => {
			if (audioTracks.has(name)) {
				console.log('Updating ', name, volume);
				const track = audioTracks.get(name);
				audioTracks.set(name, { ...track, volume });
			}
		});

		audioTracks = audioTracks;
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
		{#each _.entries(audioTracks) as [trackName, track]}
			<AudioTrack
				name={trackName}
				src={track.src}
				bind:volume={track.volume}
				maxVolume={masterVolume}
			></AudioTrack>
		{/each}
	</div>
</div>
