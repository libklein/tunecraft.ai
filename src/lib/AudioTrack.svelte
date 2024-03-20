<script lang="ts">
	import { Howl, Howler } from 'howler';
	import { onDestroy } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import Button from './components/ui/button/button.svelte';
	import { Trash } from 'lucide-svelte';
	import VolumeControl from './VolumeControl.svelte';
	import { createEventDispatcher } from 'svelte';

	export let name: string;
	export let src: string;
	export let volume: number = 0;
	export let random: boolean = false;
	export let periodDurationSeconds: number = 0;
	export let expectedPlaysPerPeriod: number = 0;
	export let maxVolume: number = 1;

	let sound: Howl | null = null;
	let nextPlayTimer: ReturnType<typeof setTimeout> | null = null;
	let _volume = [volume];
	let dispatch = createEventDispatcher();

	function createSound(src: string, random: boolean) {
		if (sound) {
			sound.unload();
		}
		sound = new Howl({
			src: [src],
			volume: 0,
			loop: !random,
			autoplay: true
		});
	}

	function scheduleNextPlay(periodDurationSeconds: number, expectedPlaysPerPeriod: number) {
		if (nextPlayTimer) {
			clearTimeout(nextPlayTimer);
		}

		const expectedWait = (periodDurationSeconds / expectedPlaysPerPeriod) * 1000;
		const nextPlay = Math.random() * 0.5 * expectedWait + 0.75 * expectedWait;

		nextPlayTimer = setTimeout(() => {
			sound && sound.play();
			scheduleNextPlay(periodDurationSeconds, expectedPlaysPerPeriod);
		}, nextPlay);
	}

	$: volume = _volume[0];
	$: scaledVolume = volume * maxVolume;
	$: createSound(src, random);
	$: sound && sound.volume(scaledVolume);
	$: sound && random && scheduleNextPlay(periodDurationSeconds, expectedPlaysPerPeriod);

	onDestroy(() => {
		if (sound) {
			sound.unload();
		}
	});
</script>

<Card.Root class="w-full">
	<Card.Header>
		<Card.Title>{name}</Card.Title>
		<!-- <Card.Description>Card Description</Card.Description> -->
	</Card.Header>
	<Card.Content class="flex flex-row">
		<VolumeControl {volume}></VolumeControl>
	</Card.Content>
	<Card.Footer>
		<Button class="w-full" on:click={() => dispatch('remove')}>
			<Trash></Trash>
		</Button>
	</Card.Footer>
</Card.Root>

<style>
	/* your styles go here */
</style>
