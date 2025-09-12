<template>
  <BaseModal
    title="Restore Canarytoken IAM role and policy"
    :has-close-button="true"
    :content-class="`items-stretch`"
  >
    <template #default>
      <div class="place-self-center w-full">
        <Form
          class="flex flex-col justify-center items-center mb-24"
          :validation-schema="schema"
          :initial-values="initialValues"
          @submit="handleGenerateSnippet"
        >
          <BaseFormTextField
            id="external_id"
            name="external_id"
            label="Add here your External ID"
            placeholder="e.g. abCd7Lb6cEZrMCEm3OAoj"
            required
            :has-arrow="true"
            arrow-variant="one"
            :arrow-word-position="2"
            class="flex-grow min-w-[300px]"
          />
          <BaseButton type="submit">Generate Snippet</BaseButton>
        </Form>
        <template v-if="showSnippet">
          <BaseSkeletonLoader
            v-if="isLoading"
            class="mt-24 h-[10svh] w-full"
          />
          <template v-else>
            <h2 class="mb-24 mt-16 text-center">
              Run the AWS CLI command below
            </h2>
            <div class="text-right">
              <BaseLabelArrow
                id="aws-snippet"
                label="Copy AWS CLI snippet"
                arrow-word-position="last"
                arrow-variant="two"
                class="z-10"
              />
            </div>
            <BaseCodeSnippet
              id="aws-snippet"
              lang="bash"
              :code="setupSnippetCommands"
              custom-height="120px"
              class="wrap-code max-w-[100%]"
            />
          </template>
          <div class="text-center flex mt-24 gap-8 items-center justify-center">
            <p>What's this snippet doing?</p>
            <button
              v-tooltip="{
                content: 'Check details',
                triggers: ['hover'],
              }"
              class="w-24 h-24 text-sm duration-150 bg-transparent border border-solid rounded-full hover:text-white hover:bg-green-600 hover:border-green-300"
              aria-label="What's this snippet doing?"
              @click="handleShowModalInfoSnippet"
            >
              <font-awesome-icon
                icon="question"
                aria-hidden="true"
              />
            </button>
          </div>
        </template>
      </div>
    </template>
    <template #footer>
      <BaseButton
        variant="secondary"
        @click="closeModal"
        >Done</BaseButton
      >
    </template>
  </BaseModal>
</template>

<script lang="ts" setup>
import { computed, ref, defineAsyncComponent } from 'vue';
import * as Yup from 'yup';
import { Form } from 'vee-validate';
import type { GenericObject } from 'vee-validate';
import { useModal } from 'vue-final-modal';
import { policyDocument } from '@/components/tokens/aws_infra/constants.ts';

const ModalInfoSnippet = defineAsyncComponent(
  () => import('./ModalInfoSnippet.vue')
);

const props = defineProps<{
  closeModal: () => void;
  roleName: string;
  externalId: string;
  managementAwsAccount: string;
  accountNumber: string;
}>();

const emits = defineEmits(['updateExternalId']);

const localExternalId = ref('');
const showSnippet = ref(false);
const isLoading = ref(false);

const initialValues = {
  external_id: props.externalId || '',
};

const setupSnippetCommands = computed(() => {
  const externalIdSnippet = props.externalId || localExternalId.value;

  return `aws iam create-role --no-cli-pager --role-name ${props.roleName} --assume-role-policy-document \'{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "arn:aws:sts::${props.managementAwsAccount}:assumed-role/InventoryManagerRole/${externalIdSnippet}"}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": "${externalIdSnippet}"}}}]}\'

aws iam create-policy --no-cli-pager --policy-name Canarytokens-Inventory-ReadOnly-Policy --policy-document \'${policyDocument}\'

aws iam attach-role-policy --role-name ${props.roleName} --policy-arn arn:aws:iam::${props.accountNumber}:policy/Canarytokens-Inventory-ReadOnly-Policy
`;
});

const schema = Yup.object().shape({
  external_id: Yup.string().required('The external ID is required'),
});

function handleGenerateSnippet(values: GenericObject) {
  localExternalId.value = values.external_id;

  if (localExternalId.value) {
    showSnippet.value = true;
    isLoading.value = true;
    emits('updateExternalId', localExternalId.value);
    setTimeout(() => {
      isLoading.value = false;
    }, 2000);
  }
}

function handleShowModalInfoSnippet() {
  const { open, close } = useModal({
    component: ModalInfoSnippet,
    attrs: {
      closeModal: () => close(),
    },
  });
  open();
}
</script>
