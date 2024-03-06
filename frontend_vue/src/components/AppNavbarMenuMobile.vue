<template>
    <button class="bg-green md:hidden w-[36px] h-[36px] rounded-full self-center mr-16" @click="handleShowMobileMenu">
        <span v-if="showMobileMenu">X</span>
        <span v-else>M</span>
    </button>
    <nav class="absolute w-full text-center md:hidden bg-green top-[80px] py-32 min-h-svh z-50" v-if="showMobileMenu">
        <ul class="uppercase">
            <li v-for="item in menuItems" :key="item.name" class="py-8">
                <RouterLink :to="item.path" class="text-green-200 hover:text-white" @click="handleShowMobileMenu">
                    {{ item.name }}
                </RouterLink>
            </li>
        </ul>
    </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router'
import type { PropType } from 'vue';

type menuItemsType = {
    name: string,
    path: string
}

defineProps({
    menuItems: {
        type: Array as PropType<menuItemsType[]>,
        required: true
    },
})

const showMobileMenu = ref(false)

function handleShowMobileMenu() {
    showMobileMenu.value = !showMobileMenu.value;
}
</script>
