<template>
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
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

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
