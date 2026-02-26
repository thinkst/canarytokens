<template>
  <div class="flex flex-col items-center gap-16 my-24 mb-16 text-center">
    <div class="mt-8 mb-40">
      <h1 class="text-4xl font-semibold text-grey-900">
        Create a Canarytoken.<br />Deploy it somewhere.
      </h1>
      <h2
        class="flex flex-row items-center justify-center gap-4 mt-16 leading-none font-md text-grey-400"
      >
        Know. When it matters.
        <a
          href="https://docs.canarytokens.org/guide"
          target="_blank"
        >
          <div
            class="inline-block w-[1.1rem] h-[1.1rem] text-xs duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300 border-grey-200 text-grey-300"
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
import { useRoute, useRouter } from 'vue-router';
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

const route = useRoute();
const router = useRouter();
const filterValue = ref('');
const searchValue = ref('');
const filteredList: Ref<TokenServicesType> = ref(tokenServices);
const animationType = ref('move-grid');
const selectedModalToken = ref<string | null>(null);
const closeCurrentModal = ref<(() => void) | null>(null);

const createRouteAliasLookup = Object.entries(tokenServices).reduce(
  (lookup: Record<string, string>, [tokenType, tokenService]) => {
    if (tokenService.createRouteTokenAlias) {
      lookup[tokenService.createRouteTokenAlias.toLowerCase()] = tokenType;
    }

    return lookup;
  },
  {}
);

function closeModalState() {
  closeCurrentModal.value = null;
  selectedModalToken.value = null;
}

function openTokenModal(selectedToken: string) {
  if (selectedModalToken.value === selectedToken) {
    return;
  }

  closeCurrentModal.value?.();

  const { open, close } = useModal({
    component: ModalToken,
    attrs: {
      selectedToken: selectedToken,
      closeModal: async (options?: { keepRoute?: boolean }) => {
        close();
        closeModalState();

        if (options?.keepRoute) {
          return;
        }

        const currentRoute = router.currentRoute.value;
        const shouldResetToHome =
          currentRoute.name === 'create' || Boolean(currentRoute.query.open);

        if (shouldResetToHome) {
          await router.push({ path: '/' });
        }
      },
    },
  });

  closeCurrentModal.value = close;
  selectedModalToken.value = selectedToken;
  open();
}

async function handleClickToken(selectedToken: string) {
  const tokenAlias = tokenServices[selectedToken].createRouteTokenAlias;
  await router.push({ path: `/create/${tokenAlias}` });
}

function getTokenFromOpenQuery(openQuery: unknown): string | null {
  if (typeof openQuery === 'string') {
    return tokenServices[openQuery] ? openQuery : null;
  }
  if (Array.isArray(openQuery)) {
    const firstToken = openQuery.find(
      (value) => typeof value === 'string' && tokenServices[value]
    );
    return firstToken ?? null;
  }
  return null;
}

function getTokenFromCreateRouteParam(tokentypeParam: unknown): string | null {
  const routeTokenCandidates =
    typeof tokentypeParam === 'string'
      ? [tokentypeParam]
      : Array.isArray(tokentypeParam)
        ? tokentypeParam.filter((value): value is string => typeof value === 'string')
        : [];

  for (const routeTokenCandidate of routeTokenCandidates) {
    const normalizedRouteToken = routeTokenCandidate.toLowerCase();
    const underscoreTokenType = normalizedRouteToken.replace(/-/g, '_');
    const resolvedTokenType =
      tokenServices[normalizedRouteToken]
        ? normalizedRouteToken
        : tokenServices[underscoreTokenType]
          ? underscoreTokenType
          : createRouteAliasLookup[normalizedRouteToken];

    if (resolvedTokenType && tokenServices[resolvedTokenType]) {
      return resolvedTokenType;
    }
  }

  return null;
}

watch(
  () => [route.query.open, route.params.tokentype],
  ([openQueryValue, createRouteTokenValue]) => {
    const tokenFromOpenQuery = getTokenFromOpenQuery(openQueryValue);

    if (tokenFromOpenQuery) {
      openTokenModal(tokenFromOpenQuery);
      return;
    }

    const tokenFromCreateRoute = getTokenFromCreateRouteParam(
      createRouteTokenValue
    );

    if (tokenFromCreateRoute) {
      openTokenModal(tokenFromCreateRoute);
      return;
    }

    if (selectedModalToken.value) {
      closeCurrentModal.value?.();
      closeModalState();
    }
  },
  { immediate: true }
);

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
