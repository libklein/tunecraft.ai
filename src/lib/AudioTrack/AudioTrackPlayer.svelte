<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Pencil, Trash } from 'lucide-svelte';
	import VolumeControl from '$lib/VolumeControl.svelte';
	import { createEventDispatcher } from 'svelte';

	export let name: string;
	export let volume: number = 0;

	let _volume = [volume];
	let dispatch = createEventDispatcher();
	let editEh = () => dispatch('edit');
	let removeEh = () => dispatch('remove');

	$: volume = _volume[0];
</script>

<Card.Root class="w-full flex flex-col justify-end">
	<Card.Header>
		<Card.Title>{name}</Card.Title>
		<!-- <Card.Description>Card Description</Card.Description> -->
	</Card.Header>
	<Card.Content class="flex flex-col">
		<VolumeControl bind:volume></VolumeControl>
	</Card.Content>
	<Card.Footer class="pb-2 grow flex flex-col justify-end">
		<Button class="w-full h-8 mb-1" on:click={editEh}>
			<Pencil></Pencil>
		</Button>
		<Button class="w-full h-8 bg-red-800 hover:bg-red-700" on:click={removeEh}>
			<Trash></Trash>
		</Button>
	</Card.Footer>
</Card.Root>
