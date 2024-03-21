<script lang="ts">
	import AudioTrack from '$lib/AudioTrack.svelte';
	import { DEFAULT_TRACK_MAP } from '$lib/tracks';
	import type { GenerateTrackMixResponse, Track } from '$lib/models';
	import { TRACK_PERIOD_DURATION_TO_SECONDS } from '$lib/models.d';
	import _ from 'lodash';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Button } from '$lib/components/ui/button';
	import { SendHorizonal } from 'lucide-svelte';
	import * as Dialog from '$lib/components/ui/dialog';
	import { onMount } from 'svelte';
	import AudioTrackSelector from '@/AudioTrackSelector.svelte';
	import VolumeControl from '@/VolumeControl.svelte';

	let masterVolume: number = 1;

	let selectedTracks: Track[] = [];
	let aiPrompt: string =
		'Relaxing music for studying with a fireplace in the background and some train noises.';
	let aiPromptFocused = false;
	let addingTrack = false;

	function focusAIPrompt() {
		aiPromptFocused = true;
	}

	function addTrack() {
		// Add a new track to the selected tracks
		addingTrack = true;
	}

	function removeTrack(track: Track) {
		// Remove a track from the selected tracks
		selectedTracks = selectedTracks.filter((t) => t !== track);
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

<!-- The prompt dialog -->
<Dialog.Root bind:open={aiPromptFocused}>
	<Dialog.Portal>
		<Dialog.Overlay />
		<Dialog.Content>
			<Textarea bind:value={aiPrompt} />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>

<!-- The add track dialog -->
<Dialog.Root bind:open={addingTrack}>
	<Dialog.Portal>
		<Dialog.Overlay />
		<Dialog.Content>TODO</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>

<div class="container flex flex-col mx-auto max-w-3xl items-center justify-center md:mt-32">
	<span class="flex flex-row w-full items-center font-light">
		<hr class="grow mr-4" />
		<span class="text-2xl text-gray-500">GENERATE USING AI</span>
		<hr class="grow ml-4" />
	</span>
	<div class="flex flex-row w-full pt-6 pb-6">
		<Input type="text" class="grow" bind:value={aiPrompt} on:focus={focusAIPrompt} />
		<Button on:click={() => getSoundMix(aiPrompt)}><SendHorizonal /></Button>
	</div>
	<div class="container w-full font-light">
		<span class="flex flex-row w-full items-center">
			<hr class="grow mr-4" />
			<span class="text-2xl text-gray-500">OR MIX YOURSELF</span>
			<hr class="grow ml-4" />
		</span>
		<VolumeControl bind:volume={masterVolume}></VolumeControl>
	</div>
	<ul class="container max-w-3xl mx-auto flex flex-row flex-wrap justify-center gap-4">
		{#each selectedTracks as track}
			<li class="w-48 h-48 flex">
				<AudioTrack
					name={track.name}
					src={track.src}
					bind:volume={track.volume}
					random={track.random}
					periodDurationSeconds={track.periodDurationSeconds}
					expectedPlaysPerPeriod={track.expectedPlaysPerPeriod}
					maxVolume={masterVolume}
					on:remove={() => removeTrack(track)}
				></AudioTrack>
			</li>
		{/each}
		<li class="w-48 h-48 flex">
			<AudioTrackSelector class="w-full" on:click={addTrack}></AudioTrackSelector>
		</li>
	</ul>
</div>
