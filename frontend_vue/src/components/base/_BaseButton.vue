<template>
    <button v-bind="$attrs" :class="buttonClass" :type="type">
        <slot></slot>
    </button>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed } from 'vue';

type variantType = 'primary' | 'secondary' | 'text';
type buttonType = 'button' | 'submit' | 'reset';

const props = defineProps({
    variant: {
        type: String as PropType<variantType>,
        default: 'primary'
    },
    type: {
        type: String as PropType<buttonType>,
        default: 'button'
    }
})


const buttonClass = computed(() => {
    switch (props.variant) {
        case 'primary':
            return 'relative bg-green hover:bg-green-300 disabled:pointer-events-none disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.25rem] focus-visible:outline-0 focus-visible:border-green-800  focus:bg-green-300 focus:border-green-800 focus:outline-0 text-white border shadow-solid-shadow-green border-green-800 font-semibold rounded-full lg:px-32 lg:py-16 px-16 py-8';
        case 'secondary':
            return 'relative bg-transparent hover:bg-green-300 disabled:pointer-events-none disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.25rem] focus-visible:outline-0 focus:bg-green-300 focus:border-green-800 focus:outline-0 text-green-800 border shadow-solid-shadow-green border-green-800 font-semibold rounded-full lg:px-32 lg:py-16 px-16 py-8';
        case 'text':
            return 'font-semibold hover:text-green-800 focus:text-green-800 text-grey-500 rounded-full px-16 py-8'
        default:
            return 'relative bg-green hover:bg-green-300 disabled:pointer-events-none disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.25rem] focus-visible:outline-0 focus-visible:border-green-800  focus:bg-green-300 focus:border-green-800 focus:outline-0 text-white border shadow-solid-shadow-green border-green-800 font-semibold rounded-full lg:px-32 lg:py-16 px-16 py-8';
    }
})

</script>
