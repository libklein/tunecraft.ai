<script lang="ts">
	import AudioTrack from '$lib/AudioTrack';
	import { DEFAULT_TRACK_MAP } from '$lib/tracks';
	import type { GenerateTrackMixResponse, Track } from '$lib/models';
	import { TRACK_PERIOD_DURATION_TO_SECONDS } from '$lib/models.d';
	import _ from 'lodash';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Button } from '$lib/components/ui/button';
	import { SendHorizonal, LoaderCircle } from 'lucide-svelte';
	import * as Dialog from '$lib/components/ui/dialog';
	import AudioTrackSelector from '$lib/AudioTrackSelector';
	import VolumeControl from '@/VolumeControl.svelte';
	import * as Alert from '$lib/components/ui/alert';
	import { ExclamationTriangle } from 'svelte-radix';
	import { Toaster } from '$lib/components/ui/sonner';
	import { toast } from 'svelte-sonner';
	import RatingPrompt from '@/RatingPrompt/RatingPrompt.svelte';

	let masterVolume: number = 1;

	let selectedTracks: Track[] = [];
	let lastMixId: string | null = null;
	const trackMap = _.cloneDeep(DEFAULT_TRACK_MAP);
	let aiPrompt: string =
		'Relaxing music for studying with a fireplace in the background and some train noises.';
	let aiPromptFocused = false;
	let loading = false;
	let error = '';
	let ratingPromptId: ReturnType<typeof toast.custom> | null = null;
	let ratingPromptTimeout: ReturnType<typeof setTimeout> | null = null;

	function focusAIPrompt() {
		aiPromptFocused = true;
	}

	function addTrack(track: Track) {
		selectedTracks = [
			...selectedTracks,
			{
				...track,
				id: Math.random().toString(36).substring(2)
			}
		];
	}

	function removeTrack(track: Track) {
		// Remove a track from the selected tracks
		selectedTracks = selectedTracks.filter((t) => t !== track);
	}

	function handlePromptKeyPress(event: KeyboardEvent) {
		// Ctrl + Enter to submit
		if (event.key === 'Enter' && event.ctrlKey) {
			aiPromptFocused = false;
			getSoundMix(aiPrompt);
		}
	}

	async function getSoundMix(aiPrompt: string) {
		loading = true;
		hideRatingPrompt();
		if (ratingPromptTimeout != null) {
			clearTimeout(ratingPromptTimeout);
		}
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

			if (!response.ok) {
				const responseBody = await response.json();
				throw new Error(responseBody.message);
			}

			trackMix = await response.json();
			error = '';
			// Show rating prompt after 5 seconds
			ratingPromptTimeout = setTimeout(() => {
				showRatingPrompt();
			}, 10000);
		} catch (e: any) {
			error = e.message;
			return;
		} finally {
			loading = false;
		}

		lastMixId = trackMix.mixId;

		// Clear the current selection
		selectedTracks = [];

		trackMix.mix
			.map((track) => {
				const trackDefinition = trackMap.get(track.name);
				if (!trackDefinition) {
					console.error(`Track ${track.name} not found in track map`);
					return;
				}
				return {
					name: track.name,
					description: trackDefinition.description,
					src: trackDefinition.src,
					volume: track.volume,
					random: track.random,
					periodDurationSeconds: TRACK_PERIOD_DURATION_TO_SECONDS[track.random_unit],
					expectedPlaysPerPeriod: track.random_counter
				};
			})
			.filter(Boolean)
			.forEach(addTrack);
	}

	async function submitRating(rating: number) {
		if (lastMixId !== null) {
			const response = await fetch('/api/rate', {
				method: 'POST',
				body: JSON.stringify({ rating, mixId: lastMixId }),
				headers: {
					'content-type': 'application/json'
				}
			});

			if (!response.ok) {
				const responseBody = await response.json();
				throw new Error(responseBody.message);
			}
		}
	}

	function hideRatingPrompt() {
		if (ratingPromptId !== null) {
			toast.dismiss(ratingPromptId);
		}
		ratingPromptId = null;
	}

	function showRatingPrompt() {
		ratingPromptId = toast.custom(RatingPrompt, {
			duration: Number.POSITIVE_INFINITY,
			onDismiss: hideRatingPrompt,
			onAutoClose: hideRatingPrompt,
			componentProps: {
				ratingCb: (value) => {
					submitRating(value);
					hideRatingPrompt();
				}
			}
		});
	}
</script>

<!-- The prompt dialog -->
<Dialog.Root bind:open={aiPromptFocused}>
	<Dialog.Portal>
		<Dialog.Overlay />
		<Dialog.Content class="p-0">
			<template slot="close"></template>
			<Textarea bind:value={aiPrompt} on:keypress={handlePromptKeyPress} />
			<div class="absolute top-full flex flex-row justify-center w-full mt-2">
				<Button on:click={() => getSoundMix(aiPrompt)}
					><SendHorizonal class="mr-2" /> Generate</Button
				>
			</div>
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
<Toaster position="bottom-center" expand class="shadow-none" />

<div class="container flex flex-col mx-auto max-w-3xl items-center justify-center h-full">
	<span class="flex flex-row w-full items-center font-light">
		<hr class="grow mr-4" />
		<span class="text-2xl text-gray-500">GENERATE USING AI</span>
		<hr class="grow ml-4" />
	</span>
	<div class="pt-6 pb-6 w-full">
		<div class="flex flex-row w-full border border-input rounded-lg">
			<Input
				type="text"
				class="grow border-none"
				bind:value={aiPrompt}
				on:focus={focusAIPrompt}
				disabled={loading}
			/>
			<Button on:click={() => getSoundMix(aiPrompt)} disabled={loading}>
				{#if loading}
					<LoaderCircle class="animate-spin" />
				{:else}
					<SendHorizonal />
				{/if}
			</Button>
		</div>
		{#if error}
			<Alert.Root class="mt-2" variant="destructive">
				<ExclamationTriangle class="h-4 w-4" />
				<Alert.Title>Error</Alert.Title>
				<Alert.Description>{error}</Alert.Description>
			</Alert.Root>
		{/if}
	</div>
	<div class="container w-full font-light">
		<span class="flex flex-row w-full items-center">
			<hr class="grow mr-4" />
			<span class="text-2xl text-gray-500">MIX YOURSELF</span>
			<hr class="grow ml-4" />
		</span>
		<div class="pb-2">
			<VolumeControl bind:volume={masterVolume}></VolumeControl>
		</div>
	</div>
	<ul class="container max-w-3xl mx-auto flex flex-row flex-wrap justify-center gap-4">
		{#each selectedTracks as track (track.id)}
			<li class="w-48 h-48 flex">
				<AudioTrack
					name={track.name}
					src={track.src}
					bind:volume={track.volume}
					bind:random={track.random}
					bind:periodDurationSeconds={track.periodDurationSeconds}
					bind:expectedPlaysPerPeriod={track.expectedPlaysPerPeriod}
					maxVolume={masterVolume}
					on:remove={() => removeTrack(track)}
				></AudioTrack>
			</li>
		{/each}
		<li class="w-48 h-48 flex">
			<AudioTrackSelector
				class="w-full grow"
				tracks={Array.of(...trackMap.values())}
				on:add={(e) => addTrack(e.detail)}
			></AudioTrackSelector>
		</li>
	</ul>
</div>
