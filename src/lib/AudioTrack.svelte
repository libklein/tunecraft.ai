<script lang="ts">
	import { Howl, Howler } from 'howler';
	import { onDestroy } from 'svelte';

	export let name: string;
	export let src: string;
	export let volume: number = 0;
	export let random: boolean = false;
	export let periodDurationSeconds: number = 0;
	export let expectedPlaysPerPeriod: number = 0;
	export let maxVolume: number = 1;

	let sound: Howl | null = null;
	let nextPlayTimer: ReturnType<typeof setTimeout> | null = null;

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

<div class="container">
	{name}:
	<input type="range" id="volume" bind:value={volume} min="0" max="1" step="0.01" />
	<label for="volume">{volume * 100}%</label>
</div>

<style>
	/* your styles go here */
</style>
