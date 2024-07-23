<!-- eslint-disable vuejs-accessibility/click-events-have-key-events -->
<!-- eslint-disable vuejs-accessibility/no-static-element-interactions -->
<template>
  <div
    class="relative flex items-center justify-center w-full"
    :class="disabled && 'pointer-events-none'"
    @dragover="handleDragOver"
    @drop="handleDrop"
    @dragleave="handleDragLeave"
  >
    <label
      ref="labelFileInput"
      for="dropzone-file"
      :class="labelClass"
      class="flex flex-col items-center justify-center w-full py-16 border border-dashed rounded-2xl"
    >
      <div class="flex flex-col items-center justify-center pt-5 pb-6">
        <FolderIcon
          class="w-[3.5rem] h-[3rem]"
          :class="[
            isDragging ? 'scale-105' : 'scale-100',
            disabled && 'grayscale',
          ]"
          :has-file="showFileName"
        ></FolderIcon>

        <p
          v-if="fileName"
          class="py-8 mb-2 text-grey-500"
        >
          {{ showFileName }}
        </p>
        <p
          v-if="isDragging"
          class="py-8 mb-2 font-semibold text-grey-500"
        >
          Drop the file! 🎤
        </p>
        <p
          v-else-if="!fileName"
          class="py-8 mb-2 text-sm text-center text-grey-500"
        >
          <span class="font-semibold"
            >Drag and drop
            <span class="font-normal">{{ infoAllowedFile }}</span>
          </span>
          <span class="block text-grey-300">or</span>
        </p>

        <BaseButton
          class="upload-button"
          :disabled="disabled"
          :variant="!showFileName ? 'secondary' : 'text'"
          @click.stop="
            showFileName ? handleFileRemove($event) : triggerFileInput($event)
          "
          >{{ showFileName ? 'Remove file' : 'Browse file' }}</BaseButton
        >
      </div>
      <p
        id="error-message"
        class="pt-16 text-sm font-semibold leading-4 text-red"
      >
        {{ errorMessage }}
      </p>
      <input
        v-bind="$attrs"
        :id="id"
        ref="fileInput"
        type="file"
        class="hidden"
        :disabled="disabled"
        @change.stop="handleFileChange"
        @blur="handleBlur"
      />
    </label>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, toRef } from 'vue';
import FolderIcon from '@/components/icons/FolderIcon.vue';
import { useField, useFieldError } from 'vee-validate';

const props = defineProps<{
  id: string;
  infoAllowedFile?: string;
  disabled?: boolean;
}>();

const emit = defineEmits(['file-selected']);

const fileInput = ref<HTMLElement | null>(null);
const labelFileInput = ref<HTMLElement | null>(null);
const fileName = ref();
const isDragging = ref(false);
const id = toRef(props, 'id');

const { value, errorMessage, handleBlur, resetField } = useField(id);
const hasErrorMessage = useFieldError(id);

onMounted(() => {
  isDragging.value = false;
});

const showFileName = computed(() => fileName.value);

const labelClass = computed(() => {
  if (hasErrorMessage.value) return 'border-red-300 hover:border-red-300';
  if (props.disabled) return 'border-grey-300 opacity-80 bg-grey-50';
  return 'border-green-600 hover:border-green-300';
});

function triggerFileInput(e: MouseEvent) {
  resetField();
  fileInput.value?.click();
  (e.target as HTMLElement)?.blur();
}

function fileUpload(file: File) {
  fileName.value = file.name;
  value.value = file;
  return emit('file-selected', file);
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  labelFileInput.value?.classList.add('bg-green-50');
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
  labelFileInput.value?.classList.remove('bg-green-50');
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  isDragging.value = false;

  if (event.dataTransfer?.files) {
    const file = event.dataTransfer.files[0];
    fileUpload(file);
    labelFileInput.value?.classList.remove('bg-green-50');
  }
}

function handleFileRemove(e: MouseEvent) {
  (e.target as HTMLElement)?.blur();

  if (fileInput.value) {
    (fileInput.value as HTMLInputElement).value = '';
    fileName.value = null;
  }
  resetField();
}

function handleFileChange(event: Event) {
  resetField();
  const input = event.target as HTMLInputElement;
  if (input.files?.length) {
    const file = input.files[0];
    fileUpload(file);
  }
}
</script>
