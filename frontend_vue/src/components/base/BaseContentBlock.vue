<template>
	<span
		class="content-block flex items-center justify-between gap-8 sm:gap-24 py-8 px-[1em] text-grey-500 border border-grey-100 rounded-xl bg-white hover:text-grey-700">
		<div class="flex items-center">
			<font-awesome-icon class="text-grey-200 mr-8 sm:mr-[.75em] text-lg sm:text-xl" aria-hidden="true" :icon="iconName" />
			<div>
				<span class="block text-xs font-light text-grey-800 mb-1.5">{{ props.label }}</span>
				<span class="block text-grey-800 font-medium" :class="{ copied }">{{ props.text }}</span>
			</div>
		</div>
		<BaseCopyButton v-if="copyContent" :content="props.text" class="ring-white ring-4" @click="handleCopyText()" />
	</span>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
	label: string;
	text: string;
	copyContent: boolean;
	iconName: string;
}>();

const copied = ref(false)

const handleCopyText = () => {
	copied.value = true;
	setTimeout(() => {
		copied.value = false;
	}, 1750);
}
</script>
<style lang="scss" scoped>
span.copied {
	background-color: #0393b3;
	color: white;
}
</style>
