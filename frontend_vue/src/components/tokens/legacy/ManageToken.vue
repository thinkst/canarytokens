<template>
  <div v-if="!props.tokenBackendResponse">Error loading</div>
<BaseMessageBox variant="warning">
  This is a legacy token that was created prior to 2017.<br/>
  These tokens alert but <strong class="font-bold">miss some meta-data</strong> that helps during incidents.<br/>
  We <strong class="font-bold">recommend replacing</strong> this older token with a current alternative.
</BaseMessageBox>
</template>

<script lang="ts" setup>
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();


</script>
