<template>
  <ModalContentHowToUseLoader v-if="isLoading" />
  <div v-else>
    <ul
      v-if="howToUseToken.length > 0"
      class="flex flex-col gap-16 my-16 ml-16 items-left text-grey-800"
    >
      <li
        v-for="item in howToUseToken"
        :key="item"
        class="grid justify-start grid-flow-col gap-8 text-left"
      >
        {{ item }}
      </li>
    </ul>
    <div v-else>
      At this time, we do not have any suggestions available. Please check back
      soon!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue';
import ModalContentHowToUseLoader from '@/components/ui/ModalContentHowToUseLoader.vue';

const props = defineProps<{
  selectedToken: string;
}>();

const howToUseToken = shallowRef([]);
const isLoading = ref(true);

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
</style>
