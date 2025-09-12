<template>
  <div class="flex flex-row items-center justify-between mt-32">
    <div class="flex flex-col">
      <span>AWS Infra Decoys</span>
      <span class="text-xs leading-4 text-grey-500 pr-[3rem]"
        >Step through the wizard to check your current decoys or make any
        required changes</span
      >
    </div>
    <div>
      <BaseButton
        class="whitespace-nowrap"
        @click="handleEditPlan"
        >Manage Decoys</BaseButton
      >
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import { useRoute, useRouter } from 'vue-router';
import { setTokenData } from '@/utils/dataService.ts';
import type { TokenDataType } from '@/utils/dataService';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

const route = useRoute();
const router = useRouter();

function handleEditPlan() {
  const { aws_region, aws_account_id, type } =
    props.tokenBackendResponse.canarydrop;
  const auth_id = route.params.auth;
  const token_id = route.params.token;

  setTokenData({
    token: token_id,
    auth_token: auth_id,
    aws_region: aws_region,
    aws_account_number: aws_account_id,
  } as TokenDataType);

  router.push({
    name: 'manage-custom',
    params: {
      tokentype: type,
    },
  });
}
</script>
