<script lang="ts">
	import { Howl } from 'howler';
	import { onDestroy } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import AudioTrackPlayer from './AudioTrackPlayer.svelte';
	import AudioTrackEditor from './AudioTrackEditor.svelte';

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
	let editing = false;
	let dispatch = createEventDispatcher();

	function createSound(src: string, random: boolean) {
		console.log('createSound', src, random);
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

	function edit() {
		editing = true;
	}

	function back() {
		editing = false;
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

<div class="flip-box h-full">
	<div class="flip-box-inner h-fll" class:flip-it={editing}>
		{#if editing}
			<div class="flip-back h-full">
				<AudioTrackEditor
					bind:name
					bind:src
					bind:volume
					bind:random
					bind:periodDurationSeconds
					bind:expectedPlaysPerPeriod
					on:back={back}
				/>
			</div>
		{:else}
			<AudioTrackPlayer bind:volume bind:name on:remove on:edit={edit} />
		{/if}
	</div>
</div>

<style>
	/* The flip box container - set the width and height to whatever you want. We have added the border property to demonstrate that the flip itself goes out of the box on hover (remove perspective if you don't want the 3D effect */
	.flip-box {
		background-color: transparent;
		width: 400px;
		height: 300px;
		/* 		border: 1px solid #ddd; */
		perspective: 1000px; /* Remove this if you don't want the 3D effect */
	}

	.flip-back {
		transform: rotateY(180deg);
	}

	/* This container is needed to position the front and back side */
	.flip-box-inner {
		position: relative;
		width: 100%;
		height: 100%;
		text-align: center;
		transition: transform 0.4s;
		transform-style: preserve-3d;
	}

	/* Do an horizontal flip on button click */
	.flip-it {
		transform: rotateY(180deg);
	}
</style>
