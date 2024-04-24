<template>
  <div
    v-if="isLoading"
    class="flex flex-col w-full gap-8 ml-32"
  >
    <BaseSkeletonLoader
      class="w-[60%]"
      type="text"
    />
    <BaseSkeletonLoader
      class="w-[30%]"
      type="text"
    />
    <BaseSkeletonLoader
      class="w-[30%]"
      type="text"
    />
    <BaseSkeletonLoader
      class="w-[50%]"
      type="text"
    />
  </div>
  <div v-else>
    <ul
      v-if="howToUseToken.length > 0"
      class="flex flex-col gap-16 my-16 fa-ul items-left intro text-grey-800"
    >
      <li
        v-for="item in howToUseToken"
        :key="item"
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
import { ref, onMounted } from 'vue';

const props = defineProps<{
  selectedToken: string;
}>();

const howToUseToken = ref([]);
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

<style>
.fa-ul > li::before {
  content: '\f059';
  font-family: 'Font Awesome 6 Free';
  color: hsl(36, 100%, 50%);
  display: inline-block;
  width: 1.5em;
  margin-left: -1.5em;
}
</style>
