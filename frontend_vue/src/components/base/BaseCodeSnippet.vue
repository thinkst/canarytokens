<template>
  <div>
    <label
      v-if="label"
      class="inline-block mb-8 text-grey-500"
      :for="label"
      >{{ label }}</label
    >

    <div class="relative bg-white border rounded-lg border-grey-100">
      <button
        v-if="showExpandButton"
        id="show-all-button"
        class="absolute w-[6rem] top-16 left-16 px-8 z-10 font-semibold text-green-600 bg-white border border-green-200 refresh-token rounded-xl hover:bg-green-50 hover:text-green-500 focus:text-green-500 focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0"
        @click="handleShowAllSnippet"
      >
        {{ showAllCode ? 'Show less' : 'Show all' }}
      </button>
      <div class="absolute top-[.8rem] right-[1rem] z-10 flex gap-8">
        <BaseRefreshButton
          v-if="hasRefresh"
          @refresh-token="handleRefreshToken"
        />
        <BaseCopyButton
          :content="code"
          class="ring-white ring-4"
        />
      </div>
      <VCodeBlock
        :id="label"
        :code="code"
        highlightjs
        :height="componentHeight"
        :lang="lang"
        theme="github"
        :copy-button="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import VCodeBlock from '@wdns/vue-code-block';

const props = withDefaults(
  defineProps<{
    code: string;
    lang: string;
    hasRefresh?: boolean;
    hasCopy?: boolean;
    showExpandButton?: boolean;
    customHeight?: string;
    label?: string | null;
  }>(),
  {
    hasRefresh: false,
    hasCopy: true,
    customHeight: null,
    label: null,
  }
);

const emits = defineEmits(['refresh-token']);
const showAllCode = ref(false);

const componentHeight = computed(() => {
  if (props.customHeight && !props.showExpandButton) {
    return props.customHeight;
  }
  return showAllCode.value ? 'auto' : props.customHeight;
});

function handleRefreshToken() {
  emits('refresh-token');
}

function handleShowAllSnippet() {
  showAllCode.value = !showAllCode.value;
}
</script>
