<template>
  <div>
    <label
      v-if="label"
      class="inline-block mb-8 text-grey-500"
      :for="label"
      >{{ label }}</label
    >

    <div class="relative border rounded-lg border-grey-100">
      <div class="absolute top-[.8rem] right-[1rem] z-10 flex gap-8">
        <BaseRefreshButton
          v-if="hasRefresh"
          @refresh-token="handleRefreshToken"
        />
        <BaseCopyButton :content="code" />
      </div>
      <VCodeBlock
        :id="label"
        :code="code"
        highlightjs
        :lang="lang"
        theme="github"
        :height="multiline ? customHeight : '3.5rem'"
        :copy-button="false"
        :class="{ 'pr-[3rem]': !multiline }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import VCodeBlock from '@wdns/vue-code-block';

withDefaults(
  defineProps<{
    code: string;
    lang: string;
    multiline?: boolean;
    hasRefresh?: boolean;
    hasCopy?: boolean;
    customHeight?: string;
    label?: string | null;
  }>(),
  {
    multiline: false,
    hasRefresh: false,
    hasCopy: true,
    customHeight: '250px',
    label: null,
  }
);

const emits = defineEmits(['refresh-token']);

function handleRefreshToken() {
  emits('refresh-token');
}
</script>
