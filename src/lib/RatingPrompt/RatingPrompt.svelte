<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Frown, Meh, Smile, X } from 'lucide-svelte';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { createEventDispatcher } from 'svelte';

	const ratings = [
		{ icon: Frown, popover: 'The mix does not fit the description', color: 'red', value: -1 },
		{ icon: Meh, popover: 'The mix is okay', color: 'yellow', value: 0 },
		{ icon: Smile, popover: 'The mix is perfect', color: 'green', value: 1 }
	];

	const dispatch = createEventDispatcher();

	export let ratingCb: (_: number) => void;
</script>

<Card.Root class="flex flex-col justify-center relative">
	<Card.Header class="pt-2 pl-4 pr-2 pb-2 flex-row items-center justify-between">
		<Card.Title class="text-l font-normal text-gray-700"
			>How happy are you with this mix?</Card.Title
		>
		<span class="ml-2">
			<button
				on:click={() => {
					dispatch('closeToast');
				}}><X class="w-4 h-4" /></button
			>
		</span>
	</Card.Header>
	<Card.Content class="flex flex-row justify-around pb-4 px-4 pt-0">
		{#each ratings as rating}
			<button
				on:click={() => {
					ratingCb(rating.value);
				}}
			>
				<svelte:component
					this={rating.icon}
					class={`hover:cursor-pointer hover:fill-${rating.color}-500`}
				/>
			</button>
			<!-- <Tooltip.Root> -->
			<!-- 	<Tooltip.Trigger asChild let:builder> -->
			<!-- 		<button -->
			<!-- 			use:builder.action -->
			<!-- 			{...builder} -->
			<!-- 			on:click={() => { -->
			<!-- 				ratingCb(rating.value); -->
			<!-- 			}} -->
			<!-- 		> -->
			<!-- 			<svelte:component -->
			<!-- 				this={rating.icon} -->
			<!-- 				class={`hover:cursor-pointer hover:fill-${rating.color}-500`} -->
			<!-- 			/> -->
			<!-- 		</button> -->
			<!-- 	</Tooltip.Trigger> -->
			<!-- 	<Tooltip.Content> -->
			<!-- 		<p>{rating.popover}</p> -->
			<!-- 	</Tooltip.Content> -->
			<!-- </Tooltip.Root> -->
		{/each}
	</Card.Content>
</Card.Root>
