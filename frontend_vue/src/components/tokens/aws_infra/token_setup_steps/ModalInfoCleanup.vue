<template>
  <BaseModal
    title="How do I clean up IAM resources for Canarytokens Inventory?"
    :has-close-button="true"
    :content-class="`items-stretch`"
  >
    <template #default>
      <h2 class="text-md mb-16 text-center">
        Copy and run these commands in your AWS CLI to fully remove the
        Canarytokens IAM role and policy.
      </h2>
      <BaseLabelArrow
        id="aws-snippet"
        label="Copy AWS Cleanup snippet"
        arrow-word-position="last"
        arrow-variant="two"
        class="z-10 text-right"
      />
      <BaseCodeSnippet
        v-if="cleanupSnippetCommands"
        lang="bash"
        :code="cleanupSnippetCommands"
        custom-height="100px"
        class="wrap-code"
      />
    </template>
    <template #footer>
      <BaseButton
        variant="primary"
        @click="closeModal"
        >Close</BaseButton
      >
    </template>
  </BaseModal>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps<{
  awsAccountNumber: string;
  roleName: string;
  customerAwsAccount: string;
  closeModal: () => void;
}>();

const cleanupSnippetCommands = computed(() => {
  return `aws iam detach-role-policy --role-name ${props.roleName} --policy-arn arn:aws:iam::${props.customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

    aws iam delete-policy --policy-arn arn:aws:iam::${props.customerAwsAccount}:policy/Canarytokens-Inventory-ReadOnly-Policy

    aws iam delete-role --role-name  ${props.roleName}`;
});

</script>
