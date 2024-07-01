<template>
  <div class="flex flex-col items-center gap-16 my-24 mb-16 text-center">
    <div class="mt-8 mb-40">
      <h1 class="text-4xl font-semibold text-grey-900">
        Create a Canarytoken, <br />Deploy it somewhere,
      </h1>
      <h2 class="mt-16 font-md text-grey-400">
        Know. When it matters.
        <a
          href="https://docs.canarytokens.org/guide"
          target="_blank"
        >
          <div
            class="inline-block w-[1.1rem] h-[1.1rem] text-xs duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300 border-grey-300 text-grey-300"
          >
            <font-awesome-icon
              icon="question"
              aria-hidden="true"
            />
            <span class="sr-only">What is this?</span>
          </div>
        </a>
      </h2>
    </div>
    <SearchFilterTokensHeader
      @filtered-list="filteredList = $event"
      @filter-search="searchValue = $event"
      @filter-category="filterValue = $event"
      @is-sql-injection="handleSolitaire"
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
          :selected-token="key"
          :title="(token as TokenServiceType).label"
          :description="(token as TokenServiceType).description"
          :logo-img-url="(token as TokenServiceType).icon"
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
import solitaireVictory from '@/utils/solitaireVictory';

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

function handleSolitaire() {
  // don't apply effect on mobile
  if (window.innerWidth <= 768) {
    return;
  }

  const tokenCard = document.querySelectorAll('.token-card-wrapper');

  tokenCard.forEach((card, index) => {
    solitaireVictory([card as HTMLElement], index);
  });
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
  position: absolute;
}
</style>
