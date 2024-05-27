<template>
  <ModalContentHowToUseLoader v-if="isLoading" />
  <template v-else>
    <ul
      v-if="howToUseToken.length > 0"
      class="flex flex-col w-full gap-16 my-16 ml-16 items-left text-grey-800"
    >
      <li
        v-for="item in parsedHowToUseToken"
        :key="item.id"
        class="grid justify-start grid-flow-col gap-8 text-left"
      >
        <component
          :is="item.component"
          v-bind="item.props"
        />
      </li>
    </ul>
    <div v-else>
      At this time, we do not have any suggestions available. Please check back
      soon!
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import ModalContentHowToUseLoader from '@/components/ui/ModalContentHowToUseLoader.vue';

const props = defineProps<{
  selectedToken: string;
}>();

const howToUseToken = ref([]);
const isLoading = ref(true);

const parsedHowToUseToken = computed(() => {
  return howToUseToken.value.map((item, index) => {
    return {
      id: index,
      component: 'p',
      props: {
        innerHTML: item,
      },
    };
  });
});

const loadHowToUse = async () => {
  const { howToUse } = await import(
    `@/components/tokens/${props.selectedToken}/howToUse.ts`
  );
  isLoading.value = false;
  howToUseToken.value = howToUse;
};

onMounted(loadHowToUse);
</script>

<style scoped>
li::before {
  content: '';
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 1rem;
  margin-top: 0.1rem;
  background-color: hsl(157, 77%, 45%);
  border: 4px solid hsl(141, 75%, 76%);
}

p >>> code {
  @apply bg-grey-100 px-8 py-[2px] rounded-md mt-4;
}
</style>
