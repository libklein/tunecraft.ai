<script lang="ts">
	import { Howl, Howler } from 'howler';
	import { onDestroy } from 'svelte';
	import { Slider } from '$lib/components/ui/slider';
	import { Label } from '$lib/components/ui/label';
	import * as Card from '$lib/components/ui/card';

	export let name: string;
	export let src: string;
	export let volume: number = 0;
	export let random: boolean = false;
	export let periodDurationSeconds: number = 0;
	export let expectedPlaysPerPeriod: number = 0;
	export let maxVolume: number = 1;

	export { _class as class };

	let sound: Howl | null = null;
	let nextPlayTimer: ReturnType<typeof setTimeout> | null = null;
	let _volume = [volume];
	let _class = '';

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

<Card.Root class={_class}>
	<Card.Header>
		<Card.Title>{name}</Card.Title>
		<!-- <Card.Description>Card Description</Card.Description> -->
	</Card.Header>
	<Card.Content>
		<Slider id="volume-slider" bind:value={_volume} min={0} max={1} step={0.01} />
		<label for="volume-slider">{volume * 100}%</label>
	</Card.Content>
	<!-- <Card.Footer> -->
	<!-- 	<p>Card Footer</p> -->
	<!-- </Card.Footer> -->
</Card.Root>

<style>
	/* your styles go here */
</style>
