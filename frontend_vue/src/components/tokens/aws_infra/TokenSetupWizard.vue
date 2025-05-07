<template>
  <p>Placeholder</p>
  {{ props.isManageToken }}
</template>

<script lang="ts" setup>
const props = defineProps<{
  isManageToken?: boolean;
}>();
</script>
