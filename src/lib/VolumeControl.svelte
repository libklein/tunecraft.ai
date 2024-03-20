<script lang="ts">
	import { Volume1, Volume2, VolumeX } from 'lucide-svelte';
	import { Slider } from '$lib/components/ui/slider';
	import { Label } from '$lib/components/ui/label';
	import Button from './components/ui/button/button.svelte';

	export let volume: number = 0;
	let _volume = [volume];
	let _lastVolume = 0;

	$: volume = _volume[0];

	function mute() {
		_lastVolume = volume;
		_volume = [0];
	}

	function unmute() {
		_volume = [_lastVolume];
	}
</script>

<span class="flex flex-row w-full items-center">
	<button on:click={() => (volume == 0 ? unmute() : mute())}>
		{#if volume > 0.5}
			<Volume2 />
		{:else if volume > 0}
			<Volume1 />
		{:else}
			<VolumeX />
		{/if}
	</button>
	<Slider class="grow ml-2" id="volume-slider" bind:value={_volume} min={0} max={1} step={0.01} />
	<!-- <Label for="volume-slider">{volume * 100}%</Label> -->
</span>
