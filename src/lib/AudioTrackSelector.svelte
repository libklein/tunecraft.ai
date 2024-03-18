<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Plus } from 'lucide-svelte';

	export { _class as class };

	let _class = '';
</script>

<Card.Root class={_class}>
	<Card.Content class="flex justify-center items-center w-full h-full p-20"
		><Plus class="w-full h-full" /></Card.Content
	>
</Card.Root>

<style>
	/* your styles go here */
</style>
