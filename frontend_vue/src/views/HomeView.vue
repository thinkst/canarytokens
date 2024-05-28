<template>
  <div class="flex flex-col items-center gap-16 my-24 mb-16 text-center">
    <div>
      <h1 class="text-4xl font-semibold text-grey-900">
        Here goes something, like a
        <span class="text-green-500">clear</span> Headline.
      </h1>
      <h2 class="mt-8 font-md text-grey-400">
        Something else we want to tell users when they land here.
      </h2>
      <h3 class="mt-32 mb-16 text-xl text-grey-800">
        Generate new Canarytoken
      </h3>
    </div>
    <SearchFilterTokensHeader
      @filtered-list="filteredList = $event"
      @filter-search="searchValue = $event"
      @filter-category="filterValue = $event"
    />
  </div>
  <!--Tokens Grid -->
  <!-- No elements found -->
  <template v-if="Object.keys(filteredList).length === 0">
    <p class="text-xl text-center text-grey-400">
      Nothing found for "{{ searchValue }}"
      {{ filterValue ? `in category "${filterValue}"` : '' }}
    </p>
  </template>

  <!--Tokens Grid -->
  <!-- Grid elements -->
  <AppLayoutGrid>
    <TransitionGroup
      :name="animationType"
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
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import { tokenServices } from '@/utils/tokenServices';
import type {
  TokenServicesType,
  TokenServiceType,
} from '@/utils/tokenServices';
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import CardToken from '@/components/ui/CardToken.vue';
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';
import SearchFilterTokensHeader from '@/components/SearchFilterTokensHeader.vue';

const filterValue = ref('');
const searchValue = ref('');
const filteredList: Ref<TokenServicesType> = ref(tokenServices);
const animationType = ref('move-grid');

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

watch(filterValue, (newVal, oldVal) => {
  if (oldVal === '') {
    animationType.value = 'move-grid';
  }
  if (newVal === '') {
    animationType.value = 'move-grid';
  }
  if (newVal !== '' && oldVal !== '') {
    animationType.value = 'fade';
  }
});
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
  transition: all 0.3s cubic-bezier(0.55, 0, 0.1, 1);
}

.fade-move,
.fade-enter-active,
.fade-leave-active {
  transition: all 1s cubic-bezier(0.55, 0, 0.1, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(30px, 0);
}

.fade-leave-active {
  opacity: 0;
  transition: all 0.2s cubic-bezier(0.55, 0, 0.1, 1);
  transform: translate(30px, 0);
}
</style>
