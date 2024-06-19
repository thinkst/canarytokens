<template>
  <ModalContentHowToUseLoader v-if="isLoading" />
  <template v-else>
    <div class="flex flex-col w-full md:w-[100%] lg:w-[80%] sm:mt-40 px-8">
      <HowDoesItWorkSteps :selected-token="props.selectedToken" />
      <h2 class="mt-40 text-center text-grey-800">
        Ideas for
        <span class="font-semibold"
          >{{ tokenServices[$props.selectedToken].label }} token</span
        >
        use :
      </h2>
      <ul
        v-if="howToUseToken.length > 0"
        class="flex flex-col w-full gap-16 p-16 my-16 bg-white border items-left text-grey-800 border-grey-200 rounded-xl"
      >
        <li
          v-for="item in parsedHowToUseToken"
          :key="item.id"
          class="grid justify-start grid-flow-col gap-8 px-16 py-8 text-left text-grey-500"
        >
          <component
            :is="item.component"
            v-bind="item.props"
          />
        </li>
      </ul>
      <div v-else>
        At this time, we do not have any suggestions available. Please check
        back soon!
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import ModalContentHowToUseLoader from '@/components/ui/ModalContentHowToUseLoader.vue';
import HowDoesItWorkSteps from '@/components/ui/HowDoesItWorkSteps.vue';
import { tokenServices } from '@/utils/tokenServices';

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
  font-family: 'Font Awesome 6 Free';
  content: '\f0e7';
  @apply text-green-500;
}

p :deep(code) {
  @apply bg-green-100 px-8 py-[2px] rounded-md mt-4;
  overflow-wrap: anywhere;
}
</style>
