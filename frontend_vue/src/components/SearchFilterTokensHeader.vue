<template>
  <div
    class="flex flex-col items-center justify-between w-full gap-24 md:flex-row"
  >
    <ul class="flex flex-row flex-wrap gap-8 list-none justify-left">
      <FilterButton
        id="filterAll"
        category="All"
        category-type="Canarytokens"
        :selected="!filterValue"
        @click="filterValue = ''"
      />
      <li
        v-for="category in TOKEN_CATEGORY"
        :key="category"
      >
        <FilterButton
          :category="category"
          category-type="Canarytokens"
          :selected="filterValue === category"
          @click="handleFilterByCategory(category)"
        />
      </li>
    </ul>
    <SearchBar
      placeholder="Search"
      :value="searchValue"
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
import type { TokenServicesType } from '@/utils/tokenServices';
import { tokenServices } from '@/utils/tokenServices';
import SearchBar from '@/components/ui/SearchBar.vue';
import FilterButton from '@/components/ui/FilterButton.vue';
import { TOKEN_CATEGORY } from '@/components/constants.ts';
import { sqlInjectionPattern } from '@/utils/utils';
import { debounce } from '@/utils/utils';

const emits = defineEmits([
  'filtered-list',
  'filter-category',
  'filter-search',
  'is-sql-injection',
]);

const filterValue = ref('');
const searchValue = ref('');

const filteredList: ComputedRef<TokenServicesType> = computed(() => {
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

function filterBySearch(list: TokenServicesType): TokenServicesType {
  if (!searchValue.value) {
    return list;
  }
  return Object.entries(list).reduce<TokenServicesType>((acc, [key, val]) => {
    if (val.label.toLowerCase().includes(searchValue.value.toLowerCase())) {
      return { ...acc, [key]: val };
    }
    if (
      Array.isArray(val.keywords) &&
      val.keywords.some((keyword) =>
        keyword.toLowerCase().includes(searchValue.value.toLowerCase())
      )
    ) {
      return { ...acc, [key]: val };
    }
    return acc;
  }, {});
}

function filterByCategory(list: TokenServicesType): TokenServicesType {
  if (!filterValue.value) {
    return list;
  }
  return Object.entries(list).reduce<TokenServicesType>((acc, [key, val]) => {
    if (
      Array.isArray(val.category) &&
      val.category.includes(filterValue.value)
    ) {
      return { ...acc, [key]: val };
    } else if (val.category === filterValue.value) {
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
  if (sqlInjectionPattern.test(searchValue.value)) {
    filterValue.value = '';
    searchValue.value = '';
    // wait for debounce on searchValue
    setTimeout(() => {
      searchValue.value === '' && emits('is-sql-injection', true);
    }, 300);
    return;
  }
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
