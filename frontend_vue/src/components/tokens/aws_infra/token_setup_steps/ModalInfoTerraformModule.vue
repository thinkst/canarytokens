m
<template>
  <BaseModal
    title="How do I use this module?"
    :has-close-button="true"
    :content-class="`items-stretch`"
  >
    <template #default>
      <div>
        <BaseBulletList
          :list="infoList"
          class="mt-24 wrap-code"
        />
      </div>
    </template>
    <template #footer>
      <BaseButton
        variant="primary"
        @click="closeModal"
        >All clear!</BaseButton
      >
    </template>
  </BaseModal>
</template>

<script lang="ts" setup>
defineProps<{
  closeModal: () => void;
}>();

const infoList = ['Something', 'Something else', 'Something more!'];
</script>
