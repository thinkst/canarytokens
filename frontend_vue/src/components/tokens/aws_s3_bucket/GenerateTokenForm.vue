<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="aws_s3_bucket_name"
      type="text"
      placeholder="e.g. internal-backup-prod"
      label="S3 Bucket Name"
      full-width
      required
    />
    <button
      type="button"
      class="flex flex-row items-center self-end gap-8 px-8 py-4 mb-8 text-xs border rounded-full w-fit grow-0 text-grey-400 border-grey-200 hover:text-green-500 hover:border-green-500"
      @click.prevent="showSuggester = !showSuggester"
    >
      <font-awesome-icon
        :icon="!showSuggester ? 'plus' : 'minus'"
      ></font-awesome-icon>
      {{ showSuggester ? 'Hide Suggestions' : 'Not sure? Generate a name' }}
    </button>
    <div
      v-if="showSuggester"
      class="flex flex-col gap-8"
    >
      <div class="flex flex-col gap-4">
        <label class="ml-4 text-sm font-semibold"
          >Enter a keyword to generate available bucket names</label
        >
        <input
          v-model="keyword"
          type="text"
          placeholder="e.g. acme, internal, staging"
          class="w-full px-16 py-8 text-sm border rounded-3xl border-grey-400 shadow-inner-shadow-grey focus-visible:outline-green-500"
          @keyup.enter="fetchSuggestions"
        />
      </div>
      <base-button
        variant="secondary"
        class="self-end"
        :disabled="loading"
        @click.prevent="fetchSuggestions"
      >
        {{ loading ? 'Checking...' : 'Suggest' }}
      </base-button>
      <div
        v-if="suggestions.length"
        class="flex flex-wrap gap-4"
      >
        <button
          v-for="name in suggestions"
          :key="name"
          type="button"
          class="px-8 py-4 text-xs border rounded-full cursor-pointer border-grey-200 hover:text-green-500 hover:border-green-500"
          @click="pickSuggestion(name)"
        >
          {{ name }}
        </button>
      </div>
      <p
        v-if="noResults"
        class="text-xs text-grey-400"
      >
        No available bucket names found. Try a different keyword.
      </p>
    </div>
    <BaseFormSelect
      id="aws_s3_region"
      label="AWS Region"
      :options="AWS_REGIONS"
      placeholder="Select AWS region"
      required
      searchable
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="S3 bucket token in prod AWS account (us-east-1)"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useField } from 'vee-validate';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { AWS_REGIONS } from '@/components/tokens/aws_infra/constants';
import { suggestS3BucketNames } from '@/api/main';

const showSuggester = ref(false);
const keyword = ref('');
const suggestions = ref<string[]>([]);
const loading = ref(false);
const noResults = ref(false);

const { setValue: setBucketName } = useField('aws_s3_bucket_name');

async function fetchSuggestions() {
  const kw = keyword.value.trim();
  if (!kw || loading.value) return;

  loading.value = true;
  noResults.value = false;
  suggestions.value = [];

  try {
    const response = await suggestS3BucketNames(kw);
    suggestions.value = response.data.suggestions || [];
    noResults.value = suggestions.value.length === 0;
  } catch {
    noResults.value = true;
  } finally {
    loading.value = false;
  }
}

function pickSuggestion(name: string) {
  setBucketName(name);
  showSuggester.value = false;
  suggestions.value = [];
}
</script>
