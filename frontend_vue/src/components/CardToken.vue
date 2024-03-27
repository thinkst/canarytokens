<template>
  <li class="relative flex">
    <button
      class="relative border flex-1 group flex flex-col px-24 py-32 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out token-card"
      @click.stop="handleClickToken"
    >
      <img
        :src="getImgUrl(tokenLogoUrl)"
        class="h-[4rem]"
        aria-hidden="true"
        :alt="`${title} logo`"
      />
      <span class="py-16 font-semibold leading-5 text-center text-grey-800">
        {{ title }}
      </span>
      <span class="leading-5 text-left text-grey-400 text-balance">
        {{ description }}
      </span>
      <span
        class="absolute border-none group-hover:right-[8px] group-focus:right-[8px] hover:right-[8px] focus:right-[8px] focus:opacity-100 py-8 px-8 focus:border opacity-0 right-[0] bottom-[0] group-hover:opacity-100 group-focus:opacity-100 transition-all"
      >
        <font-awesome-icon
          icon="arrow-right"
          class="text-green-500"
          aria-hidden="true"
        />
        <span class="fa-sr-only">Add {{ title }}</span>
      </span>
    </button>

    <BaseLinkDocumentation
      :link="documentationLink"
      class="absolute z-10 top-[9px] left-[8px] cursor-pointer transition-all duration-100 ease-in-out token-card__documentation-link"
      tabindex="0"
      :title="title"
    />
  </li>
</template>

<script setup lang="ts">
import useImage from '@/composables/useImage';

const emit = defineEmits(['clickToken']);

const props = withDefaults(
  defineProps<{
    description: string;
    title: string;
    logoImgUrl: string;
    documentationLink: string;
  }>(),
  {
    logoImgUrl: 'default.png',
  }
);

const { getImgUrl } = useImage();

const tokenLogoUrl = `token_icons/${props.logoImgUrl}`;

function handleClickToken() {
  emit('clickToken');
}
</script>

<style scoped>
.token-card:hover + .token-card__documentation-link,
.token-card:focus + .token-card__documentation-link,
.token-card:focus-visible + .token-card__documentation-link {
  top: -0.2em;
}

.token-card:hover,
.token-card:focus {
  @apply border-green top-[-0.45em] shadow-solid-shadow-green-500-md;
}
</style>
