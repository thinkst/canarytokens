<template>
  <div class="paginated_object_list__wrapper">
    <fieldset
      class="paginated_object_list"
      :style="{
        '--page-count': totalPagesNumber,
        '--list-rows': totalPagesNumber > 1 ? MAX_PER_PAGE : fields.length,
        '--scroll-position': `${scrollPosition}`,
        '--container-width': `${containerWidth}px`,
      }"
    >
      <!-- Slot Form -->
      <slot></slot>
    </fieldset>
  </div>
  <div
    v-if="totalPagesNumber > 1"
    class="flex flex-col items-center"
  >
    <div class="mt-16 flex flex-row gap-16">
      <button
        type="button"
        :disabled="currentPageNumber === 1"
        class="text-grey-200 hover:text-green-500 pointer"
        @click.stop="handlePreviousPage"
      >
        <span class="sr-only">Prev</span>
        <font-awesome-icon
          icon="chevron-left"
          aria-hidden="true"
        />
      </button>
      <button
        v-for="page in totalPagesNumber"
        :key="page"
        class="w-[1.5rem] h-[1.5rem] border border-solid border-grey-300 rounded-full text-sm text-grey-400 hover:text-green-500 pointer"
        type="button"
        @click.stop="currentPageNumber = page"
      >
        <span
          :class="{ 'text-grey-700 font-semibold': currentPageNumber === page }"
          >{{ page }}</span
        >
      </button>
      <button
        type="button"
        :disabled="currentPageNumber === totalPagesNumber"
        class="text-grey-200 hover:text-green-500 pointer"
        @click.stop="handleNextPage"
      >
        <span class="sr-only">Next</span>
        <font-awesome-icon
          icon="chevron-right"
          aria-hidden="true"
        />
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps<{
  fields: any;
}>();

const MAX_PER_PAGE = 10;
const currentPageNumber = ref(1);
const containerWidth = ref(0);

const totalPagesNumber = computed(() => {
  return Math.ceil(props.fields.length / MAX_PER_PAGE);
});

onMounted(() => {
  checkContainerWidth();
  window.addEventListener('resize', () => checkContainerWidth());
});

const scrollPosition = computed(() => {
  return (currentPageNumber.value - 1) * containerWidth.value;
});

function checkContainerWidth() {
  const element = document.querySelector('.paginated_object_list__wrapper');
  containerWidth.value =
    element instanceof HTMLElement ? element.offsetWidth : 0;
}

function handlePreviousPage() {
  if (currentPageNumber.value >= 1) {
    currentPageNumber.value--;
  }
}

function handleNextPage() {
  if (currentPageNumber.value < totalPagesNumber.value) {
    currentPageNumber.value++;
  }
}
</script>

<style lang="scss">
.paginated_object_list__wrapper {
  overflow: hidden;
  opacity: 0;
  animation: fadeIn 0.5s ease-in-out forwards;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.paginated_object_list {
  --page-count: 1;
  --list-rows: 8;
  --container-width: 0px;
  --scroll-position: 0;

  display: grid;
  grid-template-rows: repeat(var(--list-rows), 1fr);
  grid-template-columns: repeat(var(--page-count), var(--container-width));
  grid-auto-flow: column;
  transform: translateX(calc(var(--scroll-position) * -1px));
  transition: 150ms ease-in;
}
</style>
