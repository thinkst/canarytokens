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
      class="flex flex-col items-center justify-center w-full py-16 border border-dashed rounded-lg cursor-pointer"
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
          class=""
          :disabled="disabled"
          :variant="!showFileName ? 'secondary' : 'text'"
          @click.stop="
            showFileName ? handleFileRemove($event) : triggerFileInput($event)
          "
          >{{ showFileName ? 'Remove file' : 'Browse file' }}</BaseButton
        >
      </div>
      <p
        v-if="isNotValidFile"
        id="error-message"
        class="pt-16 text-sm font-semibold leading-4 text-red"
      >
        {{ isNotValidFileMessage }}
      </p>
      <p
        v-if="hasError"
        id="error-message"
        class="pt-16 text-sm font-semibold leading-4 text-red"
      >
        {{ errorMessage }}
      </p>
      <input
        v-bind="$attrs"
        id="dropzone-file"
        ref="fileInput"
        type="file"
        :accept="allowedFiles"
        class="hidden"
        :disabled="disabled"
        :max-size="maxSize"
        @change.stop="handleFileChange"
      />
    </label>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { convertBytes } from './utils.ts';
import FolderIcon from '@/components/icons/FolderIcon.vue';

const props = defineProps<{
  allowedFiles: string;
  infoAllowedFile: string;
  hasError?: boolean;
  errorMessage?: string;
  disabled?: boolean;
  maxSize?: number;
}>();

const emit = defineEmits(['file-selected', 'file-upload-error']);

const fileInput = ref<HTMLElement | null>(null);
const labelFileInput = ref<HTMLElement | null>(null);
const fileName = ref();
const isDragging = ref(false);
const isNotValidFile = ref(false);
const isNotValidFileMessage = ref('');

onMounted(() => {
  isNotValidFile.value = false;
  isDragging.value = false;
});

const showFileName = computed(() => fileName.value);

const labelClass = computed(() => {
  if (props.hasError || isNotValidFile.value)
    return 'border-red-300 hover:border-red-300';
  if (props.disabled) return 'border-grey-300 opacity-80 bg-grey-50';
  return 'border-green-600 hover:border-green-300';
});

function triggerFileInput(e: MouseEvent) {
  isNotValidFile.value = false;
  fileInput.value?.click();
  (e.target as HTMLElement)?.blur();
}

function fileValidation(file: File) {
  const allowedFileTypes = props.allowedFiles
    .split(',')
    .map((type) => type.trim());

  if (!allowedFileTypes.includes(file.type)) {
    isNotValidFile.value = true;
    isNotValidFileMessage.value = `${file.type} files are not allowed`;
    return emit('file-upload-error', file);
  } else if (props.maxSize && file.size > props.maxSize) {
    isNotValidFile.value = true;
    isNotValidFileMessage.value = `The file is too big. The maximum allowed size is ${convertBytes(props.maxSize)}`;
    return emit('file-upload-error', file);
  } else {
    fileName.value = file.name;
    return emit('file-selected', file);
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  isNotValidFile.value = false;

  labelFileInput.value?.classList.add('bg-green-50');
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
  isNotValidFile.value = false;

  labelFileInput.value?.classList.remove('bg-green-50');
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  isNotValidFile.value = false;
  isDragging.value = false;

  if (event.dataTransfer?.files) {
    const file = event.dataTransfer.files[0];
    fileValidation(file);

    labelFileInput.value?.classList.remove('bg-green-50');
  }
}

function handleFileRemove(e: MouseEvent) {
  (e.target as HTMLElement)?.blur();
  isNotValidFile.value = false;

  if (fileInput.value) {
    (fileInput.value as HTMLInputElement).value = '';
    fileName.value = null;
  }
}

function handleFileChange(event: Event) {
  isNotValidFile.value = false;
  const input = event.target as HTMLInputElement;
  if (input.files?.length) {
    const file = input.files[0];
    fileValidation(file);
  }
}
</script>
