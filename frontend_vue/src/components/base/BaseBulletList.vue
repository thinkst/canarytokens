<template>
  <ul class="flex flex-col w-full gap-16 my-16 items-left text-grey-800">
    <BaseBulletListItem
      v-for="item in props.list"
      :key="item"
    >
      {{ item }}
    </BaseBulletListItem>
  </ul>
</template>

<script lang="ts" setup>
const props = defineProps<{
  list: string[];
}>();
</script>
