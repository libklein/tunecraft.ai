<script lang="ts">
	export let name: string;
	export let src: string;
	export let volume: number = 0;
</script>

<div class="container">
	{name}:
	<input type="range" id="volume" bind:value={volume} min="0" max="1" step="0.01" />
	<label for="volume">{volume * 100}%</label>
	<audio {src} loop bind:volume autoplay> </audio>
</div>

<style>
	/* your styles go here */
</style>
