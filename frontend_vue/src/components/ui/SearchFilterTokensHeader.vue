<template>
  <SearchBar
    placeholder="Which Canarytoken do you need?"
    label="Search Canarytoken"
    class="w-full lg:w-[30vw] md:w-[50vw]"
    @input="
      (e: Event) =>
        debounce(
          () => (searchValue = (e.target as HTMLInputElement).value),
          250
        )()
    "
  />
  <div class="flex flex-row gap-16">
    <button @click="handleFilterByCategory('')">Remove filter</button>
    <button @click="handleFilterByCategory(TOKEN_CATEGORY.PIZZA)">Pizza</button>
    <button @click="handleFilterByCategory(TOKEN_CATEGORY.PASTA)">Pasta</button>
    <button @click="handleFilterByCategory(TOKEN_CATEGORY.GELATO)">
      Gelato
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { ComputedRef } from 'vue';
import type {
  TokenServicesType,
  TokenServiceType,
} from '@/utils/tokenServices';
import { tokenServices } from '@/utils/tokenServices';
import SearchBar from '@/components/ui/SearchBar.vue';
import { TOKEN_CATEGORY } from '@/components/constants.ts';

const emits = defineEmits([
  'filtered-list',
  'filter-category',
  'filter-search',
]);

const filterValue = ref('');
const searchValue = ref('');

function debounce(fn: () => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>;
  return () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delay);
  };
}

const filteredList: ComputedRef<
  TokenServicesType | [string, TokenServiceType]
> = computed(() => {
  const filteredByCategory = filterByCategory(tokenServices);
  const filteredBySearch = filterBySearch(tokenServices);

  if (!filterValue.value && !searchValue.value) {
    return tokenServices;
  }

  if (filterValue.value && !searchValue.value) {
    return filteredByCategory;
  }

  if (!filterValue.value && searchValue.value) {
    return filteredBySearch;
  }

  return filterBySearch(filteredByCategory);
});

function filterBySearch(list: TokenServicesType) {
  if (!searchValue.value) {
    return list;
  } else {
    return Object.entries(list).reduce((acc, [key, val]) => {
      if (val.label.toLowerCase().includes(searchValue.value.toLowerCase())) {
        return { ...acc, [key]: val };
      }
      return acc;
    }, {});
  }
}

function filterByCategory(list: TokenServicesType) {
  if (!filterValue.value) {
    return list;
  } else {
    return Object.entries(list).reduce((acc, [key, val]) => {
      if (val.category === filterValue.value) {
        return { ...acc, [key]: val };
      }
      return acc;
    }, {});
  }
}

function handleFilterByCategory(category: string) {
  filterValue.value = category;
}

watch(filteredList, () => {
  emits('filtered-list', filteredList.value);
});

watch(filterValue, () => {
  emits('filter-category', filterValue.value);
});

watch(searchValue, () => {
  emits('filter-search', searchValue.value);
});
</script>
