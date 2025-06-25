<template>
  <BaseModal
    title="What's this snippet doing?"
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

const infoList = [
  'This step grants Canarytokens.org temporary, read-only access to list names of various AWS resources (S3 buckets, SQS queues, SSM parameters, Secrets Manager secrets, DynamoDB tables, and IAM roles) to create a customized infrastructure plan.',
  'This access is automatically revoked by Canarytokens.org after plan creation.',
  'You will be provided with cleanup instructions at the end of the wizard to remove the associated AWS policy, attachment, and role.',
];
</script>
