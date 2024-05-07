<template>
  <div class="flex flex-col items-center gap-32 my-24 text-center">
    <div>
      <h1 class="text-4xl font-semibold text-grey-900">
        Here goes something, like a
        <span class="text-green-500">clear</span> Headline.
      </h1>
      <h2 class="mt-8 font-md text-grey-400">
        Something else we want to tell users when they land here.
      </h2>
      <h3 class="mt-32 text-xl text-grey-800">Generate new Canarytoken</h3>
    </div>
    <SearchBar
      placeholder="Which Canarytoken do you need?"
      label="Search Canarytoken"
      class="w-full lg:w-[30vw] md:w-[50vw]"
      @input="
        (e: Event) =>
          debounce(
            () => (searchValue = (e.target as HTMLInputElement).value),
            500
          )()
      "
    />
    {{ searchValue }}
    <div class="flex flex-row gap-16">
      <button @click="filterValue = ''">Remove filter</button>
      <button @click="filterValue = TOKEN_CATEGORY.PIZZA">Pizza</button>
      <button @click="filterValue = TOKEN_CATEGORY.PASTA">Pasta</button>
      <button @click="filterValue = TOKEN_CATEGORY.GELATO">Gelato</button>
    </div>
  </div>
  <AppLayoutGrid>
    <TransitionGroup
      :name="filterValue === '' ? 'move-grid' : 'fade-items'"
      class="relative"
    >
      <template
        v-for="(token, key) in filteredList"
        :key="key"
      >
        <CardToken
          :title="(token as TokenServiceType).label"
          :description="(token as TokenServiceType).description"
          :logo-img-url="(token as TokenServiceType).icon"
          :documentation-link="(token as TokenServiceType).documentationLink"
          @click-token="() => handleClickToken(key as string)"
        />
      </template>
    </TransitionGroup>
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ComputedRef } from 'vue';
import { TOKEN_CATEGORY } from '@/components/constants.ts';
import { tokenServices } from '@/utils/tokenServices';
import type {
  TokenServicesType,
  TokenServiceType,
} from '@/utils/tokenServices';
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import CardToken from '@/components/ui/CardToken.vue';
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';
import SearchBar from '@/components/ui/SearchBar.vue';

const filterValue = ref('');
const searchValue = ref('');

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

function handleClickToken(selectedToken: string) {
  const { open, close } = useModal({
    component: ModalToken,
    attrs: {
      selectedToken: selectedToken,
      closeModal: () => close(),
    },
  });
  open();
}

function debounce(fn: () => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>;
  return () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delay);
  };
}
</script>

<style scoped>
.move-grid-enter {
  opacity: 0;
}

.move-grid-enter-active {
  transition: all 1s;
}

.move-grid-leave {
  opacity: 0;
}

.move-grid-leave-active {
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(0);
  position: absolute;
}

.move-grid-move {
  transition: all 0.3s cubic-bezier(0.77, 0, 0.175, 1);
}

.fade-items-enter-active,
.fade-items-leave-active {
  transition: all 0.3s;
  opacity: 1;
}

.fade-items-enter,
.fade-items-leave-to {
  opacity: 0;
}
</style>
