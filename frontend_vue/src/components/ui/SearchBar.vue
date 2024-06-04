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
      v-model="model"
      type="text"
      :placeholder="placeholder"
      class="placeholder:font-thin py-8 px-[2.5rem] border font-semibold resize-none shadow-inner-shadow-grey rounded-3xl border-grey-200"
    />
    <font-awesome-icon
      icon="magnifying-glass"
      class="absolute top-[.8rem] left-16 text-grey-300 search-icon duration-150"
    ></font-awesome-icon>
    <button
      v-if="model && model.length > 0"
      class="absolute top-[.5rem] right-16 text-grey-300 duration-150 cursor-pointer hover:text-green-500"
      @click="clearInput">
      <font-awesome-icon icon="close"></font-awesome-icon>
    </button>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
defineProps<{
  placeholder: string;
  label: string;
}>();

const emits = defineEmits(['clear-search-input']);

const model = defineModel<string>();

const searchbarRef = ref();

onMounted(() => {
  searchbarRef.value.focus();
});

const clearInput = () => {
  model.value = '';
  emits('clear-search-input')
}
</script>

<style scoped>
#search-canarytoken:focus + .search-icon {
  @apply text-green-500;
}
</style>
