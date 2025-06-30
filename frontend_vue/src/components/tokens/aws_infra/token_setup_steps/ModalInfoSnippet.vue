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
  'This step grants Canarytokens.org temporary read-only access to fetch the names of your S3 buckets, SQS queues, SSM parameters, Secrets Manager secrets, DynamoDB tables, and IAM roles. We do this to create a customized set of decoy resources that apply to you.',
  'When we’re done with creating the decoy resource configuration at the end of this wizard, we will delete the ExternalID from our database. This revokes our ability to access your account.',
  'You’ll be provided with cleanup instructions at the end of the wizard to remove the associated AWS policy, attachment, and role. You should perform these steps, even though we no longer will have access to your account.',
];
</script>
