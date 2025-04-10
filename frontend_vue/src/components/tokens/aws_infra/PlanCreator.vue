<template>
  <Form
    v-slot="{ values, setFieldValue }"
    class="w-[80%] flex flex-col"
    :initial-values="initialValues.assets"
    :validation-schema="schema"
    @submit="onSubmit"
  >
    <FieldArray
      v-slot="{
        fields: buckets,
        push: pushBucket,
        remove: removeBucket,
      }: {
        fields: FieldEntry<S3BucketType | unknown>[];
        push: (value: unknown) => void;
        remove: (index: number) => void;
      }"
      name="S3Bucket"
    >
      <div class="flex justify-between items-center mb-16">
        <h3 class="font-semibold text-grey-400 text-xl">S3 Buckets</h3>
        <BaseButton
          icon="plus"
          type="button"
          :disabled="isMaxBuckets(values as AssetsTypes)"
          @click.stop="
            handleAddInstance(pushBucket, INSTANCE_DATA[INSTANCE_TYPE.S3BUCKET])
          "
          >Add Bucket</BaseButton
        >
      </div>
      <div class="grid md:grid-cols-1 xl:grid-cols-2 gap-24">
        <fieldset
          v-for="(bucket, index) in buckets"
          :key="bucket.key"
          class="border bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 justify-between items-center p-24 mb-24"
        >
          <div class="flex justify-between items-center mb-24">
            <div class="flex flex-row gap-16 justify-between items-center">
              <img
                :src="
                  getImageUrl(`aws_infra_icons/${INSTANCE_TYPE.S3BUCKET}.svg`)
                "
                alt="logo-s3-bucket"
                class="rounded-full h-[2.5rem] w-[2.5rem]"
              />
              <legend class="text-md font-semibold text-grey-400">
                S3Bucket #{{ index + 1 }}
              </legend>
            </div>
            <BaseButton
              icon="xmark"
              variant="danger"
              type="button"
              @click="handleRemoveInstance(removeBucket, index)"
              >Remove Bucket</BaseButton
            >
          </div>
          <PlanCreatorTextField
            :id="`bucket_name_${index}`"
            v-model="(buckets[index].value as S3BucketType).bucket_name"
            :name="`S3Bucket[${index}].bucket_name`"
            label="S3Bucket Name"
            :has-remove="false"
            @handle-regenerate-instance.stop="
              async (event, name) =>
                await handleRegenerateInstancetName(
                  INSTANCE_TYPE.S3BUCKET_OBJECT,
                  name,
                  setFieldValue
                )
            "
          />
          <FieldArray
            v-slot="{ fields: objects, push: pushObj, remove: removeObj }"
            :name="`S3Bucket[${index}].objects`"
          >
            <ul
              class="border-grey-300 border border-solid rounded-3xl p-16 mt-16"
            >
              <li class="flex justify-between items-center mb-16">
                <h4 class="text-md font-semibold text-grey-400">Objects</h4>
                <BaseButton
                  icon="plus"
                  @click.stop="
                    handleAddInstance(
                      pushObj,
                      INSTANCE_DATA[INSTANCE_TYPE.S3BUCKET_OBJECT]
                    )
                  "
                  >Add Object</BaseButton
                >
              </li>
              <fieldset
                v-for="(object, indexObj) in objects"
                :key="(object as unknown as S3ObjectType).object_path"
              >
                <PlanCreatorTextField
                  :id="`${index}_objects_path_${indexObj}`"
                  v-model="
                    (buckets[index].value as S3BucketType).objects[indexObj]
                      .object_path
                  "
                  :name="`S3Bucket[${index}].objects[${indexObj}].object_path`"
                  label="Object Path"
                  :has-remove="true"
                  @handle-remove-instance.stop="
                    handleRemoveInstance(removeObj, indexObj)
                  "
                  @handle-regenerate-instance.stop="
                    async (event, name) =>
                      await handleRegenerateInstancetName(
                        INSTANCE_TYPE.S3BUCKET_OBJECT,
                        name,
                        setFieldValue
                      )
                  "
                />
              </fieldset>
            </ul>
          </FieldArray>
        </fieldset>
      </div>
    </FieldArray>
    <BaseButton
      v-if="!isLoading"
      class="mt-40 self-center"
      type="submit"
    >
      Save Plan</BaseButton
    >
  </Form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Form, FieldArray } from 'vee-validate';
import type { FieldEntry } from 'vee-validate';
import * as yup from 'yup';
import {
  INSTANCE_TYPE,
  INSTANCE_DATA,
} from '@/components/tokens/aws_infra/constants.ts';
// import { generateDataChoice } from '@/api/main.ts';
import getImageUrl from '@/utils/getImageUrl';
import PlanCreatorTextField from '@/components/tokens/aws_infra/PlanCreatorTextField.vue';
import type {
  PlanValueTypes,
  S3ObjectType,
  S3BucketType,
  AssetsTypes,
} from './types';

const props = defineProps<{
  proposedPlan: PlanValueTypes;
  token: string;
  authToken: string;
}>();

const emits = defineEmits(['submitPlan']);
const isLoading = ref();
const initialValues = ref<PlanValueTypes>({ assets: { S3Bucket: [] } });

function isMaxBuckets(formValues: AssetsTypes) {
  return formValues.S3Bucket.length >= 10;
}

function handleRemoveInstance(
  callback: (index: number) => void,
  index: number
) {
  callback(index);
  console.log('event', event);
}

function handleAddInstance(
  callback: (instance: S3BucketType | S3ObjectType) => void,
  instanceType: S3BucketType | S3ObjectType
) {
  callback(instanceType);
}

async function handleRegenerateInstancetName(
  fieldType: string,
  name: string,
  setFieldValue: (field: string, value: any) => void
) {
  return setFieldValue(name, 'test placeholder!');

  // try {
  //   const res = await generateDataChoice(
  //     props.token,
  //     props.authToken,
  //     fieldType,
  //     'somethingsomething'
  //   );
  //   if (res.status !== 200) {
  //     // something
  //   }
  // } catch (err) {
  // } finally {
  //   // replace existing value
  //   console.log('done!');
  // }
}

function onSubmit(values: any) {
  emits('submitPlan', { assets: values });
  // console.log(JSON.stringify(values, null, 2));
}

watch(
  () => props.proposedPlan,
  (newPlan) => {
    initialValues.value = newPlan;
  },
  { immediate: true }
);

const schema = yup.object().shape({
  S3Bucket: yup
    .array()
    .of(
      yup.object().shape({
        bucket_name: yup.string().required().label('Bucket Name'),
        objects: yup.array().of(
          yup.object().shape({
            object_path: yup.string().required().label('Object Path'),
          })
        ),
      })
    )
    .strict(),
});
</script>
