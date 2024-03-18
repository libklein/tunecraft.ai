<script lang="ts">
	import AudioTrack from '$lib/AudioTrack.svelte';
	import { DEFAULT_TRACK_MAP } from '$lib/tracks';
	import type { GenerateTrackMixResponse, Track } from '$lib/models';
	import { TRACK_PERIOD_DURATION_TO_SECONDS } from '$lib/models.d';
	import _ from 'lodash';
	import { Slider } from '$lib/components/ui/slider';
	import { Separator } from '$lib/components/ui/separator';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import * as Dialog from '$lib/components/ui/dialog';
	import { onMount } from 'svelte';
	import AudioTrackSelector from '@/AudioTrackSelector.svelte';

	let _masterVolume: number[] = [1];
	$: masterVolume = _masterVolume[0];

	let selectedTracks: Track[] = [];
	let aiPrompt: string =
		'Relaxing music for studying with a fireplace in the background and some train noises.';
	let aiPromptFocused = false;

	function focusAIPrompt() {
		aiPromptFocused = true;
	}

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

		selectedTracks = trackMix
			.map((track) => {
				const trackDefinition = DEFAULT_TRACK_MAP.get(track.name);
				if (!trackDefinition) {
					console.error(`Track ${track.name} not found in track map`);
					return;
				}
				return {
					...trackDefinition,
					...track,
					volume: track.volume / 100,
					random: track.random,
					periodDurationSeconds: TRACK_PERIOD_DURATION_TO_SECONDS[track.random_unit],
					expectedPlaysPerPeriod: track.random_counter
				};
			})
			.filter(Boolean) as Track[];
	}

	onMount(() => {
		getSoundMix(aiPrompt);
	});
</script>

<Dialog.Root bind:open={aiPromptFocused}>
	<Dialog.Portal>
		<Dialog.Overlay />
		<Dialog.Content>
			<Textarea bind:value={aiPrompt} />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>

<div class="container flex flex-col mx-auto max-w-3xl items-center justify-center">
	<Input type="text" bind:value={aiPrompt} on:focus={focusAIPrompt} />
	<button on:click={() => getSoundMix(aiPrompt)}></button>
	<div class="container max-w-3xl mx-auto">
		<Separator />
		<Slider bind:value={_masterVolume} min={0} max={1} step={0.01} />
	</div>
	<ul class="container max-w-3xl mx-auto flex flex-row flex-wrap justify-center gap-4">
		{#each selectedTracks as track}
			<li class="w-48 h-48 flex">
				<AudioTrack
					class="w-full"
					name={track.name}
					src={track.src}
					bind:volume={track.volume}
					random={track.random}
					periodDurationSeconds={track.periodDurationSeconds}
					expectedPlaysPerPeriod={track.expectedPlaysPerPeriod}
					maxVolume={masterVolume}
				></AudioTrack>
			</li>
		{/each}
		<li class="w-48 h-48 flex"><AudioTrackSelector class="w-full"></AudioTrackSelector></li>
	</ul>
</div>
