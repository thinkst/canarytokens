<template>
  <ul class="flex flex-col gap-16 my-16 fa-ul items-left intro text-grey-800">
    <li
      v-for="item in howToUseToken"
      :key="item"
    >
      {{ item }}
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  selectedToken: string;
}>();

const howToUseToken = ref([]);

const loadHowToUse = async () => {
  const { howToUse } = await import(
    `@/components/tokens/${props.selectedToken}/howToUse.ts`
  );

  howToUseToken.value = howToUse;
};

loadHowToUse();
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
