<template>
  <BaseModal
    title="Edit account information"
    :has-close-button="true"
    :hide-footer="true"
  >
    <template #default>
      <div class="min-w-[250px] lg:w-[30vw] max-w-[400px]">
        <Form
          class="flex flex-col"
          :validation-schema="schema"
          @submit="onSubmit"
        >
          <div class="lg:basis-6/12">
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
          </div>
          <BaseMessageBox
            v-if="isError"
            variant="danger"
            >{{ isErrorMessage }}</BaseMessageBox
          >
          <div class="flex flex col justify-center gap-8 mt-24">
            <BaseButton
              variant="grey"
              @click="closeModal"
              >Cancel</BaseButton
            >
            <BaseButton
              variant="primary"
              type="submit"
              :loading="isLoading"
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
import type { GenericObject } from 'vee-validate';
import { AWS_REGIONS } from '@/components/tokens/aws_infra/constants.ts';
import { editAccountInfo } from '@/api/awsInfra';
import type { TokenDataType } from '@/utils/dataService';

const props = defineProps<{
  tokenData: TokenDataType;
  closeModal: () => void;
  saveData: (data: GenericObject) => void;
}>();

const selectedRegion = ref<{ value: string; label: string }[]>([]);
const selectedAWSaccount = ref('');
const isLoading = ref(false);
const isError = ref(false);
const isErrorMessage = ref('');

const schema = Yup.object().shape({
  aws_region: Yup.string().required('AWS region is required'),
  aws_account_number: Yup.string()
    .required('AWS account number is required')
    .matches(/^\d+$/, 'AWS account must be a number')
    .test(
      'len',
      'AWS account number must have 12 digits',
      (val) => val.length === 12
    ),
});

onMounted(() => {
  selectedRegion.value = AWS_REGIONS.filter((region) => {
    return region.value === props.tokenData.aws_region;
  });
  selectedAWSaccount.value = props.tokenData.aws_account_number;
});

async function onSubmit(values: GenericObject) {
  isLoading.value = true;
  // ...here goes the API call to manage endpoint...
  try {
    const res = await editAccountInfo(
      props.tokenData.token,
      props.tokenData.auth_token,
      values.aws_account_number,
      values.aws_region
    );

    if (res.status !== 200) {
      isError.value = true;
      isErrorMessage.value = res.data.message || 'Could not edit token!';
    }

    props.saveData(values);
    props.closeModal();
  } catch (err: any) {
    isError.value = true;
    isErrorMessage.value = err || 'Could not edit token!';
  } finally {
    isLoading.value = false;
  }
}
</script>
