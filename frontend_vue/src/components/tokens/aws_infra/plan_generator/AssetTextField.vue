<template>
  <div
    class="textfield-wrapper"
    :class="variant"
  >
    <BaseLabel
      v-if="!hideLabel"
      :id="id"
      >{{ props.label }}</BaseLabel
    >
    <span
      v-if="icon"
      class="icon rounded-full"
      :class="[{ 'top-[2rem]': !hideLabel }, { 'top-[0.5rem]': hideLabel }]"
      :style="{ 'background-image': `url(${iconURL})` }"
    ></span>
    <input
      :id="id"
      :value="value"
      :class="[
        { input__error: errorMessage },
        { input__disabled: disabled },
        { 'input__with-icon': icon },
      ]"
      :placeholder="placeholder"
      :aria-invalid="!!errorMessage"
      aria-describedby="helper error"
      :required="required"
      :disabled="disabled"
      @blur="handleChange"
      @input="(e) => validateIfErrorExists(e)"
    />
    <BaseSpinner
      v-if="isGenerateValueLoading"
      height="1.5rem"
      class="textfield__loading"
    />
    <div
      class="textfield__cta"
      :class="{ 'top-[2rem]': !hideLabel }"
    >
      <button
        v-if="!isGenerateValueLoading"
        v-tooltip="{
          content: 'Regenerate content',
        }"
        type="button"
        class="textfield__cta__regenerate"
        aria-label="Regenerate input content"
        @click="handleGenerateValue"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="rotate-right"
        ></font-awesome-icon>
      </button>
      <button
        v-if="hasRemove"
        v-tooltip="{
          content: 'Remove instance',
        }"
        type="button"
        class="textfield__cta__remove"
        aria-label="Remove instance"
        @click="emit('handleRemoveInstance')"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="trash"
        ></font-awesome-icon>
      </button>
    </div>
    <div class="error-message">
      <p
        v-if="errorMessage"
        id="error"
        class="text-xs leading-4 text-red"
      >
        {{ errorMessage }}
      </p>
      <p
        v-if="isGenerateValueError"
        id="error"
        class="text-xs leading-4 text-red"
      >
        {{ isGenerateValueError }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRef, computed, ref, watch } from 'vue';
import { useField } from 'vee-validate';
import getImageUrl from '@/utils/getImageUrl';
import { AssetTypesEnum } from '@/components/tokens/aws_infra/constants.ts';
import { useGenerateAssetName } from '@/components/tokens/aws_infra/plan_generator/useGenerateAssetName.ts';

type VariantType = 'small' | 'large';

const props = defineProps<{
  id: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  maxLength?: number;
  variant?: VariantType;
  icon?: string;
  hasRemove?: boolean;
  hideLabel?: boolean;
  assetType: AssetTypesEnum;
  fieldType: string;
  value?: string;
}>();

const { variant = 'large', hasRemove = false, hideLabel = false } = props;

const emit = defineEmits([
  'update:modelValue',
  'handleRemoveInstance',
  'handleRegenerateInstance',
]);
const id = toRef(props, 'id');
const { value, handleChange, errorMessage, resetField } = useField(
  id,
  undefined,
  {
    initialValue: props.value,
  }
);
const isGenerateValueError = ref('');
const isGenerateValueLoading = ref(false);

function validateIfErrorExists(e: Event) {
  if (errorMessage && errorMessage.value) handleChange(e);
}

async function handleGenerateValue() {
  isGenerateValueError.value = '';
  const {
    handleGenerateName,
    isGenerateNameError,
    isGenerateNameLoading,
    generatedName,
  } = useGenerateAssetName(props.assetType, props.fieldType);

  isGenerateValueLoading.value = isGenerateNameLoading.value;
  await handleGenerateName();
  isGenerateValueError.value = isGenerateNameError.value;
  resetField({ value: generatedName.value });
  isGenerateValueLoading.value = false;
}

const iconURL = computed(() => {
  return props.icon ? getImageUrl(props.icon) : '';
});

watch(
  () => props.value,
  (newValue) => {
    handleChange(newValue);
  }
);
</script>

<style scoped>
.hide-scrollbar {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Internet Explorer 10+ */
}
.hide-scrollbar::-webkit-scrollbar {
  /* WebKit */
  width: 0;
  height: 0;
}

.textfield-wrapper.large {
  @apply flex flex-col relative  text-grey-800;

  .icon {
  }

  input {
    @apply px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1;
  }

  .input__error {
    @apply border border-red shadow-none;
  }

  .input__disabled {
    @apply border-grey-200 bg-grey-100 shadow-none text-grey-300;
  }

  .textfield__loading {
    @apply absolute top-[2.2rem] right-[1rem];
  }

  .textfield__cta {
    @apply absolute top-[2rem] right-[0.5rem] flex gap-8;

    .textfield__cta__regenerate {
      @apply h-[2rem] w-[2rem] rounded-full bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-green-600 border border-green-200;
    }
    .textfield__cta__remove {
      @apply h-[2rem] w-[2rem] rounded-full bg-white hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:bg-green-100 focus:border-green-200 focus:outline-0 text-grey-300 border border-grey-200;
    }
  }

  .error-message {
    @apply h-[1rem] pr-8 mt-4 ml-16;
  }
}

.textfield-wrapper.small {
  @apply flex flex-col relative text-grey-800;

  input {
    @apply text-sm px-16 py-8 pl-16 pr-[4.5rem] border-b resize-none border-grey-400 hover:bg-grey-50 focus:bg-grey-50 focus-visible:bg-grey-50 focus:border-b  focus:border-green-500 focus-visible:outline-0;
  }

  .icon {
    @apply w-[1.5rem] h-[1.5rem] bg-no-repeat bg-cover absolute grayscale opacity-30 left-8;
  }

  .input__error {
    @apply border-b border-red;
  }

  .input__with-icon {
    @apply pl-40;
  }

  .textfield__loading {
    @apply absolute top-[0.5rem] right-[3rem];
  }

  .textfield__cta {
    @apply absolute hidden right-[0.5rem];

    .textfield__cta__regenerate {
      @apply h-[2rem] w-[2rem] rounded-full hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:outline-0 text-grey-300;
    }
    .textfield__cta__remove {
      @apply h-[2rem] w-[2rem] rounded-full hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:outline-0 text-grey-300;
    }
  }
  .error-message {
    @apply h-[1rem];
  }
}

.textfield-wrapper.small:hover > .textfield__cta {
  @apply flex;
}
</style>
