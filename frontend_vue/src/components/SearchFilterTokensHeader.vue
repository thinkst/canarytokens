<template>
  <div
    class="flex flex-col items-center justify-between w-full gap-24 md:flex-row"
  >
    <ul class="flex flex-row flex-wrap gap-8 list-none justify-left">
      <FilterButton
        category="All"
        :selected="!filterValue"
        @click="filterValue = ''"
      />
      <li
        v-for="category in TOKEN_CATEGORY"
        :key="category"
      >
        <FilterButton
          :category="category"
          :selected="filterValue === category"
          @click="handleFilterByCategory(category)"
        />
      </li>
    </ul>
    <SearchBar
      placeholder="Search"
      label="Search"
      class="w-full md:w-[15vw]"
      :class="{
        stress: searchValue.includes('!!!'),
        love: searchValue.includes('love'),
      }"
      @input="
        (e: Event) =>
          debounce(
            () => (searchValue = (e.target as HTMLInputElement).value),
            250
          )()
      "
      @clear-search-input="searchValue = ''"
    />
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
import FilterButton from '@/components/ui/FilterButton.vue';
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
  }
  return Object.entries(list).reduce((acc, [key, val]) => {
    if (val.label.toLowerCase().includes(searchValue.value.toLowerCase())) {
      return { ...acc, [key]: val };
    }
    return acc;
  }, {});
}

function filterByCategory(list: TokenServicesType) {
  if (!filterValue.value) {
    return list;
  }
  return Object.entries(list).reduce((acc, [key, val]) => {
    if (val.category === filterValue.value) {
      return { ...acc, [key]: val };
    }
    return acc;
  }, {});
}

function handleFilterByCategory(category: string) {
  if (category === filterValue.value) {
    return (filterValue.value = '');
  }
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

<style scoped>
@keyframes shake {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-3px);
  }
  50% {
    transform: translateX(3px);
  }
  75% {
    transform: translateX(-3px);
  }
  100% {
    transform: translateX(0);
  }
}

.stress {
  animation: shake 0.15s infinite;
}

.love::before {
  content: '\f004';
  font-family: 'Font Awesome 6 Free';
  font-weight: 900;
  display: inline-block;
  position: absolute;
  top: 0.5rem;
  left: -2rem;
  color: pink;
  @apply animate-ping;
}
</style>
