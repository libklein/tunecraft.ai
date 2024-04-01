<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { StepBack } from 'lucide-svelte';
	import VolumeControl from '$lib/VolumeControl.svelte';
	import { createEventDispatcher } from 'svelte';
	import Input from '@/components/ui/input/input.svelte';
	import { Separator } from '@/components/ui/separator';
	import { Switch } from '$lib/components/ui/switch';
	import { Label } from '@/components/ui/label';

	export let name: string;
	export let src: string;
	export let volume: number = 0;
	export let random: boolean = false;
	export let periodDurationSeconds: number = 1;
	export let expectedPlaysPerPeriod: number = 1;

	let _volume = [volume];
	let dispatch = createEventDispatcher();
	let backEh = () => dispatch('back');

	$: volume = _volume[0];
</script>

<Card.Root class="w-full h-full flex flex-col justify-start">
	<Card.Header class="pb-0 pt-2">
		<Card.Title class="pt-0 w-full text-nowrap truncate">{name}</Card.Title>
	</Card.Header>
	<Card.Content class="flex flex-col pb-0 pt-0">
		<VolumeControl bind:volume></VolumeControl>
		<Separator></Separator>
		<span class="flex justify-between items-center py-1">
			<Label for="playRandom">Random</Label>
			<Switch class="mr-1" bind:checked={random} id="playRandom"></Switch>
		</span>
		<div class="grow flex flex-col">
			<div class="flex items-center">
				<Label for="expectedPlaysPerPeriod">Repeat</Label>
				<Input
					type="number"
					class="border-none px-2 py-0 ring-none bg-gray-200 mx-1 h-auto grow"
					bind:value={expectedPlaysPerPeriod}
					id="expectedPlaysPerPeriod"
					min="1"
					disabled={!random}
				></Input>
			</div>
			<span>
				{expectedPlaysPerPeriod == 1 ? 'time' : 'times'} every
			</span>
			<div class="flex items-center">
				<Input
					type="number"
					bind:value={periodDurationSeconds}
					class="border-none px-2 py-0 ring-none bg-gray-200 mr-1 h-auto grow"
					id="periodDurationSeconds"
					min="1"
					disabled={!random}
				/>
				<Label for="periodDurationSeconds">seconds</Label>
				<!--
				<Select.Root disabled={!random}>
					<Select.Trigger class="w-[180px]">
						<Select.Value placeholder="unit" />
					</Select.Trigger>
					<Select.Content>
						<Select.Group>
							{#each units as unit}
								<Select.Item value={unit.value} label={unit.label}>{unit.label}</Select.Item>
							{/each}
						</Select.Group>
					</Select.Content>
				</Select.Root>
      -->
			</div>
		</div>
	</Card.Content>
	<Card.Footer class="pb-2 mt-2 grow flex flex-col justify-end">
		<Button class="w-full h-8" on:click={backEh}>
			<StepBack></StepBack>
		</Button>
	</Card.Footer>
</Card.Root>
