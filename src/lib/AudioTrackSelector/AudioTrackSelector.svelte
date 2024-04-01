<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Plus, AudioWaveformIcon, Volume1 } from 'lucide-svelte';
	import { MagnifyingGlass } from 'svelte-radix';
	import { Howl, Howler } from 'howler';
	import type { Track } from '$lib/models';
	import _ from 'lodash';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Input } from '$lib/components/ui/input';
	import { onDestroy } from 'svelte';
	import VolumeControl from '@/VolumeControl.svelte';
	import { createEventDispatcher } from 'svelte';

	function createSound(src: string) {
		if (sound) {
			sound.unload();
		}
		sound = new Howl({
			src: [src],
			volume: volume,
			loop: true,
			autoplay: true
		});
	}

	export { _class as class };
	export let tracks: Track[];

	let _class = '';
	let dialogOpen = false;
	let search = '';
	let selectedTrack: Track | null = null;
	let sound: Howl | null = null;
	let volume = 1;
	let dispatch = createEventDispatcher();

	$: selectedTrack && createSound(selectedTrack.src);
	$: selectedTrack || sound?.unload();
	$: sound && sound.volume(volume);

	$: filteredTracks = _.filter(tracks, (track) =>
		track.name.toLowerCase().includes(search.toLowerCase())
	);

	function addTrack() {
		if (selectedTrack) {
			dialogOpen = false;
			dispatch('add', selectedTrack);
			selectedTrack = null;
		}
		stopSound();
	}

	function focusTrack(evt: MouseEvent) {
		evt.target?.focus();
	}

	function stopSound() {
		sound?.unload();
	}

	onDestroy(stopSound);
</script>

<!-- The add track dialog -->
<Dialog.Root bind:open={dialogOpen}>
	<Dialog.Content class="h-64 p-0 pt-4 flex flex-col">
		<Dialog.Header class="pl-4 pr-4 grow-0"><Dialog.Title>Add track</Dialog.Title></Dialog.Header>
		<div
			class="flex flex-row items-center justify-start border-gray-150 border-t border-b px-3 grow-0"
		>
			<MagnifyingGlass class="mr-2 h-4 w-4 shrink-0 opacity-50" />
			<Input
				bind:value={search}
				placeholder="Search..."
				class="outline-none border-none shadow-none focus-visible:ring-transparent"
			></Input>
		</div>
		<div class="ml-2 mr-4">
			<VolumeControl bind:volume></VolumeControl>
		</div>
		<ScrollArea class="pl-2 pr-2 grow">
			<div class="font-light text-xs justify-center flex flex-row">
				{filteredTracks.length} tracks
			</div>
			{#each filteredTracks as track}
				<button
					class={(() => {
						return selectedTrack !== track
							? 'p-2 hover:bg-gray-100 flex flex-row items-center rounded w-full focus-visible:outline-none'
							: 'p-2 hover:bg-gray-100 bg-gray-100 flex flex-row items-center rounded w-full  focus-visible:outline-none';
					})()}
					on:click={addTrack}
					on:focus={() => {
						selectedTrack = track;
					}}
					on:mouseenter={focusTrack}
				>
					<AudioWaveformIcon class="mr-2 h-4 w-4 shrink-0 opacity-50" />
					{track.name}
					{#if selectedTrack === track}
						<Volume1 class="ml-auto h-4 w-4 shrink-0 opacity-50" />
					{/if}
				</button>
			{/each}
		</ScrollArea>
	</Dialog.Content>
</Dialog.Root>

<Card.Root
	class={_class + ' hover:cursor-pointer hover:drop-shadow'}
	on:click={() => {
		dialogOpen = true;
	}}
>
	<Card.Content class="flex justify-center items-center w-full h-full p-20"
		><Plus class="w-full h-full" /></Card.Content
	>
</Card.Root>
