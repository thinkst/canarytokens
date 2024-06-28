<template>
	<span
		class="flex items-center justify-between gap-16 md:gap-24 py-8 px-[1em] text-grey-500 border border-grey-200 rounded-xl hover:bg-white hover:text-grey-700">
		<div>
			<span class="block text-xs font-medium text-grey-800 mb-1.5">{{ props.label }}:</span>
			<span class="block" :class="{ copied }">{{ props.text }}</span>
		</div>
		<BaseCopyButton
			v-if="copyContent"
			:content="props.text"
			class="ring-white ring-4"
			@click="handleCopyText()"
		/>
	</span>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
	label: string;
	text: string;
	copyContent: boolean;
}>();

const copied = ref(false)

const handleCopyText = () => {
	copied.value = true;
	setTimeout(() => {
		copied.value = false;
	}, 1750);
}
</script>
<style>
span.copied {
	background-color: #0393b3;
	color: white;
}
</style>
