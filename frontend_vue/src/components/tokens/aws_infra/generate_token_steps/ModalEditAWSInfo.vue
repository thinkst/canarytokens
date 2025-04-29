<template>
  <BaseModal
    title="Edit Account informations"
    :has-close-button="hasCloseButton"
    :hide-footer="true"
    :content-class="`items-stretch`"
  >
    <template #default>
      <div>
        <Form
          class="flex flex-col"
          :validation-schema="schema"
          @submit="onSubmit"
          @invalid-submit="onInvalidSubmit"
        >
          <BaseFormTextField
            id="aws_account_number"
            type="text"
            placeholder="e.g. 012345678901"
            label="AWS account number"
            full-width
            required
            :value="selectedAWSaccount"
          />
          <div>
            <BaseFormSelect
              id="aws_region"
              label="AWS Region"
              :options="AWS_REGIONS"
              placeholder="Select AWS region"
              required
              searchable
              :value="selectedRegion[0]"
            />
          </div>
          <div class="flex flex col justify-center gap-8 mt-24">
            <BaseButton
              variant="grey"
              @click="closeModal"
              >Cancel</BaseButton
            >
            <BaseButton
              variant="primary"
              type="submit"
              >Save</BaseButton
            >
          </div>
        </Form>
      </div>
    </template>
  </BaseModal>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import * as Yup from 'yup';
import { Form } from 'vee-validate';
import { AWS_REGIONS } from '@/components/tokens/aws_infra/constants.ts';

const props = defineProps<{
  accountNumber: Record<string, any>;
  accountRegion: Record<string, any>;
  closeModal: () => void;
}>();

const selectedRegion = ref('');
const selectedAWSaccount = ref('');

const schema = Yup.object().shape({
  aws_region: Yup.string().required('AWS region is required'),
  aws_account_number: Yup.number()
    .typeError('AWS account must be a number')
    .required('AWS account number is required')
    .test(
      'len',
      'AWS account number must have 12 digits',
      (val) => val.toString().length === 12
    ),
});

onMounted(() => {
  selectedRegion.value = AWS_REGIONS.filter((region) => {
    return region.value === props.accountRegion;
  });
  selectedAWSaccount.value = props.accountNumber;
});

function onSubmit(values) {
  console.log('values', values);
}

function onInvalidSubmit(values: GenericObject) {
  console.log('values', values.values);
}
</script>
