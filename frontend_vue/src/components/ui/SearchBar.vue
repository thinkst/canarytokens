<template>
  <div class="relative">
    <label
      for="search-cnarytoken"
      class="sr-only"
      >{{ label }}</label
    >
    <input
      id="search-canarytoken"
      ref="searchbarRef"
      v-bind="$attrs"
      :value="value"
      type="text"
      :placeholder="placeholder"
      class="placeholder:font-thin px-[2rem] border font-semibold resize-none shadow-inner-shadow-grey rounded-3xl border-grey-200 h-32"
    />
    <font-awesome-icon
      icon="magnifying-glass"
      class="absolute top-[.5rem] left-8 text-grey-200 search-icon duration-150"
    ></font-awesome-icon>
    <button
      v-if="value && value.length > 0"
      id="clearSearchInput"
      class="absolute top-[.25rem] right-16 text-grey-300 duration-150 cursor-pointer hover:text-green-500"
      @click="clearInput"
    >
      <font-awesome-icon
        icon="close"
        aria-hidden="true"
      ></font-awesome-icon>
      <span class="fa-sr-only">Clear search</span>
    </button>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
defineProps<{
  placeholder: string;
  label: string;
  value: string;
}>();

const emits = defineEmits(['clear-search-input']);

const searchbarRef = ref();

onMounted(() => {
  searchbarRef.value.focus();
});

const clearInput = () => {
  emits('clear-search-input');
};
</script>

<style scoped>
#search-canarytoken:focus + .search-icon {
  @apply text-green-500;
}
</style>
