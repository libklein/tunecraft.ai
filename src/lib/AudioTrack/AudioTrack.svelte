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

<div class="flip-box w-full h-full max-h-full">
	<div class="flip-box-inner w-full h-full max-h-full" class:flip-it={editing}>
		{#if editing}
			<div class="flip-back w-full h-full max-h-full">
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
	.flip-box {
		background-color: transparent;
		perspective: 1000px;
	}

	.flip-back {
		transform: rotateY(180deg);
	}

	.flip-box-inner {
		position: relative;
		text-align: center;
		transition: transform 0.4s;
		transform-style: preserve-3d;
	}

	.flip-it {
		transform: rotateY(180deg);
	}
</style>
