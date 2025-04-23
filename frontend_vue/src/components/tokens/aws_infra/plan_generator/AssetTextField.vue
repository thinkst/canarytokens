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
      class="icon"
      :class="[{ 'top-[2rem]': !hideLabel }, { 'top-[0.5rem]': hideLabel }]"
      :style="{ 'background-image': `url(${iconURL})` }"
    ></span>
    <input
      :id="id"
      v-model="value"
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
    <div
      class="textfield__cta"
      :class="{ 'top-[2rem]': !hideLabel }"
    >
      <!-- Regenerate content btn -->
      <button
        v-tooltip="{
          content: 'Regenerate content',
        }"
        type="button"
        class="textfield__cta__regenerate"
        aria-label="Regenerate input content"
        @click="emit('handleRegenerateInstance', $event, props.id)"
      >
        <font-awesome-icon
          aria-hidden="true"
          icon="rotate-right"
        ></font-awesome-icon>
      </button>
      <!-- Remove instance -->
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
        v-show="errorMessage"
        id="error"
        class="text-xs leading-4 text-red"
      >
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRef, computed } from 'vue';
import { useField } from 'vee-validate';
import getImageUrl from '@/utils/getImageUrl';

type VariantType = 'small' | 'large';

const props = defineProps<{
  id: string;
  // name: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  maxLength?: number;
  variant?: VariantType;
  icon?: string;
  hasRemove?: boolean;
  hideLabel?: boolean;
}>();

const { variant = 'large', hasRemove = false, hideLabel = false } = props;

const emit = defineEmits([
  'update:modelValue',
  'handleRemoveInstance',
  'handleRegenerateInstance',
]);
const id = toRef(props, 'id');

const { value, handleChange, errorMessage } = useField(id);

function validateIfErrorExists(e: Event) {
  if (errorMessage && errorMessage.value) handleChange(e);
}

const iconURL = computed(() => {
  return props.icon ? getImageUrl(props.icon) : '';
});
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
    @apply text-sm px-8 py-8 pr-[4.5rem] border-b resize-none border-grey-400 hover:bg-grey-50 focus:bg-grey-50 focus-visible:bg-grey-50 focus:border-b  focus:border-green-500 focus-visible:outline-0;
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

  .textfield__cta {
    @apply absolute hidden right-[0.5rem];

    .textfield__cta__regenerate {
      @apply h-[2rem] w-[2rem] rounded-full hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:outline-0 text-grey-300;
    }
    .textfield__cta__remove {
      @apply h-[2rem] w-[2rem] rounded-full hover:bg-green-50 hover:text-green-500 focus:text-green-500 disabled:bg-grey-200 disabled:shadow-solid-shadow-grey disabled:border-grey-300 disabled:text-grey-400 active:shadow-none active:top-[0.15rem] focus-visible:outline-0 focus:outline-0 text-grey-300;
    }
  }
}

.textfield-wrapper.small:hover > .textfield__cta {
  @apply flex;
}
</style>
