<template>
  <div
    class="min-h-[40vh] flex flex-col gap-24 p-24 bg-grey-50 rounded-3xl items-center"
  >
    <ul
      class="sm:grid sm:grid-cols-[3fr_1fr_3fr_1fr_3fr] flex flex-row max-w-[800px]"
    >
      <template
        v-for="(step, index) in steps"
        :key="step.id"
      >
        <li
          class="flex flex-row items-center flex-1 sm:justify-start sm:flex-col elements icon relative"
        >
          <img
            :src="getImageUrl(step.icon)"
            :alt="step.alt"
            class="h-auto sm:w-[8rem]"
          />
        </li>
        <template v-if="index < steps.length - 1">
          <span
            :class="step.arrowClass"
            class="elements"
          >
            <img
              :src="getImageUrl(step.arrow)"
              alt="arrow"
              class="arrow hidden sm:flex"
            />
          </span>
        </template>
      </template>
    </ul>
    <h2 class="text-center mt-24">
      This is a multi-step token. <br />Here's the steps this wizard follows to
      quickly, safely and painlessly create the Canarytoken:
    </h2>
    <div class="mb-16">
      <BaseBulletList
        :list="stepDescription"
        class="md:max-w-[50vw]"
      />
      <p class="text-sm m-0 p-0 text-center">
        ¹We send limited inventory data to Google Gemini to generate realistic
        decoy names.
      </p>
    </div>
    <BaseButton
      class="mb-24"
      @click="emits('startTokenSetup')"
      >Good to go?</BaseButton
    >
  </div>
</template>

<script lang="ts" setup>
import getImageUrl from '@/utils/getImageUrl';

const emits = defineEmits<{
  (e: 'startTokenSetup'): void;
}>();

const steps = [
  {
    id: 1,
    icon: 'aws_infra_icons/step01.png',
    alt: 'Step 1: AWS IAM role creation icon',
    arrow: 'howitworks_arrow_1.png',
    arrowClass: 'flex items-start mt-[1rem]',
  },
  {
    id: 2,
    icon: 'aws_infra_icons/step02.png',
    alt: 'Step 2: Account scanning and AI analysis icon',
    arrow: 'howitworks_arrow_2.png',
    arrowClass: 'flex items-center',
  },
  {
    id: 3,
    icon: 'aws_infra_icons/step03.png',
    alt: 'Step 3: Terraform deployment and monitoring icon',
    arrow: '',
    arrowClass: '',
  },
];

const stepDescription = [
  `1. You'll create a read-only IAM role in your AWS account and grant us access to it.`,
  `2. We use that role to scan your account and then use an LLM¹ to suggest decoy resources.`,
  `3. We give you a Terraform module to apply in your environment, which creates the decoys. You get alerts whenever someone interacts with the decoys.`,
];
</script>

<style lang="scss" scoped>
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.arrow {
  transform: scale(2.5);
}

.icon:after {
  content: '';
  position: absolute;
  display: inline-block;
  bottom: -0.5rem;
  left: 50%;
  width: 4rem;
  height: 0.5rem;
  border-radius: 50%;
  --tw-bg-opacity: 1;
  background-color: hsl(156 9% 89% / var(--tw-bg-opacity));
  filter: blur(0.1rem);
  transform: translate(-50%, 0.2rem);
}

.elements {
  opacity: 0;

  @for $i from 1 through 5 {
    &:nth-child(#{$i}) {
      animation: fade-in 0.3s ease-in forwards;
      animation-delay: #{$i * 200}ms;
    }
  }
}
</style>
