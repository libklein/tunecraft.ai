<script lang="ts">
	import { Volume1, Volume2, VolumeX } from 'lucide-svelte';
	import { Slider } from '$lib/components/ui/slider';

	export let volume: number = 0;
	let _volume = [volume];
	let _lastVolume = 0;
	let hoversIcon = false;

	$: volume = _volume[0];
	$: indicatorIcon = getIcon(volume, hoversIcon);

	function mute() {
		_lastVolume = volume;
		_volume = [0];
	}

	function unmute() {
		_volume = [_lastVolume];
	}

	function getIcon(volume: number, hovers: boolean) {
		if (hovers) {
			return volume == 0 ? getIcon(_lastVolume, false) : VolumeX;
		} else {
			return volume == 0 ? VolumeX : volume > 0.5 ? Volume2 : Volume1;
		}
	}
</script>

<span class="flex flex-row w-full items-center">
	<button
		on:click={() => (volume == 0 ? unmute() : mute())}
		on:mouseenter={() => (hoversIcon = true)}
		on:mouseleave={() => (hoversIcon = false)}
		on:focusin={() => (hoversIcon = true)}
		on:focusout={() => (hoversIcon = false)}
	>
		<svelte:component this={indicatorIcon}></svelte:component>
	</button>
	<Slider class="grow ml-2" id="volume-slider" bind:value={_volume} min={0} max={1} step={0.01} />
	<!-- <Label for="volume-slider">{volume * 100}%</Label> -->
</span>
