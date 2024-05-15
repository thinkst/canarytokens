<template>
  <div class="relative">
    <font-awesome-icon
      icon="magnifying-glass"
      class="absolute top-[.8rem] left-16 text-grey-300"
    ></font-awesome-icon>
    <label
      for="search-cnarytoken"
      class="sr-only"
      >Search CanaryToken</label
    >
    <input
      id="search-cnarytoken"
      v-bind="$attrs"
      v-model="model"
      type="text"
      placeholder="Search Canarytoken"
      class="placeholder:font-thin py-8 pl-[2.5rem] border font-semibold resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 outline-offset-4"
    />
  </div>
</template>

<script lang="ts" setup>
defineProps<{
  placeholder: string;
  label: string;
}>();

const model = defineModel<string>();
</script>
