<template>
    <div class="flex justify-between @container gap-24">
        <AppLogo class="px-32 py-24" />
        <nav role="navigation" class="items-center justify-end hidden w-full pr-32 md:flex">
            <ul class="flex items-end pt-8 text-sm uppercase gap-x-24 lg:gap-x-32 font-regular">
                <li v-for="item in menuItems" :key="item.name">
                    <RouterLink :to="item.path" class="text-grey-400 hover:text-green desktop-link">
                        {{ item.name }}
                    </RouterLink>
                </li>
                <li class="cursor-pointer text-grey-400 hover:text-green">
                    <a href="#">
                        <font-awesome-icon icon="link" class="w-[0.8rem] pr-8" />Documentation
                    </a>
                </li>
            </ul>
        </nav>
        <AppNavbarMenuMobile :menuItems="menuItems" />
    </div>
</template>

<script setup lang="ts">
import AppLogo from './AppLogo.vue'
import { RouterLink } from 'vue-router'
import AppNavbarMenuMobile from './AppNavbarMenuMobile.vue'

const menuItems = [
    { name: 'Home', path: '/' },
    { name: 'Manage', path: '/manage' },
]
</script>

<style scoped lang="scss">
// there's a way to expose RouterLink classes for tailwind
// but it's quite cumbersome and I'd avoid it
// https://router.vuejs.org/guide/advanced/extending-router-link
.desktop-link {
    &.router-link-active {
        color: hsl(152, 59%, 48%);
        position: relative;

        &::after {
            content: '';
            position: absolute;
            top: -3px;
            right: -10px;
            width: 6px;
            height: 6px;
            border-radius: 3px;
            background-color: hsl(351, 85%, 44%);
        }
    }
}
</style>
