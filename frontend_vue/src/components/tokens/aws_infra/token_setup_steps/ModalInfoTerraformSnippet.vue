m
<template>
  <BaseModal
    title="How do I use this module?"
    :has-close-button="true"
    :content-class="`items-stretch`"
  >
    <template #default>
      <ul class="flex flex-col text-left gap-16">
        <BaseBulletListItem>
          Add the Terraform snippet into a new or existing Terraform
          configuration file.
        </BaseBulletListItem>
        <BaseBulletListItem>
          Run
          <span class="monospace">$ terraform init</span>
          to import the module and make it available to Terraform.
        </BaseBulletListItem>
        <BaseBulletListItem>
          Run
          <span class="monospace">$ terraform apply</span> to create the decoy
          assets.
        </BaseBulletListItem>
        <BaseBulletListItem>
          Run
          <span class="monospace">$ terraform destroy</span> to remove the decoy
          assets.
        </BaseBulletListItem>
        <BaseBulletListItem>
          You can edit and update the plan at a later stage, by using the Manage
          Canarytoken link we’ve emailed you.
        </BaseBulletListItem>
      </ul>
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
</script>

<style scoped>
.monospace {
  font-family: 'Courier New', Courier, monospace;
}
</style>
