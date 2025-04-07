<template>
  <Form
    class="w-[80%] flex flex-col mt-24"
    :initial-values="initialValues"
    :validation-schema="schema"
    @submit="onSubmit"
  >
    <FieldArray
      v-slot="{ fields: buckets, push: pushBucket, remove: removeBucket }"
      name="S3Bucket"
    >
      <div class="flex justify-between items-center mb-16">
        <h3 class="font-semibold text-grey-400 text-xl">S3 Buckets</h3>
        <BaseButton
          icon="plus"
          @click="
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
              @click="handleRemoveInstance(removeBucket, index)"
              >Remove Bucket</BaseButton
            >
          </div>
          <PlanCreatorTextField
            :id="`bucket_name_${index}`"
            v-model="buckets[index].value.bucket_name"
            :name="`S3Bucket[${index}].bucket_name`"
            label="S3Bucket Name"
            :has-remove="false"
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
                  @click="
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
                :key="object.indexObj"
              >
                <PlanCreatorTextField
                  :id="`${index}_objects_path_${indexObj}`"
                  v-model="buckets[index].value.objects[indexObj].object_path"
                  :name="`S3Bucket[${index}].objects[${indexObj}].object_path`"
                  label="Object Path"
                  :has-remove="true"
                  @handle-remove-instance="
                    handleRemoveInstance(removeObj, indexObj)
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
import { ref } from 'vue';
import { Form, FieldArray } from 'vee-validate';
import * as yup from 'yup';
import {
  INSTANCE_TYPE,
  INSTANCE_DATA,
} from '@/components/tokens/aws_infra/constants.ts';
import getImageUrl from '@/utils/getImageUrl';
import PlanCreatorTextField from '@/components/tokens/aws_infra/PlanCreatorTextField.vue';

const isLoading = ref();
const emits = defineEmits(['updateStep']);

const initialValues = {
  S3Bucket: [
    {
      bucket_name: 'decoy-bucket-1',
      objects: [
        {
          object_path: 'foo/bar/object1',
        },
      ],
    },
    {
      bucket_name: 'decoy-bucket-2',
      objects: [
        { object_path: 'moo/bar/object1' },
        { object_path: 'moo/bar/object2' },
        { object_path: 'moo/bar/object3' },
      ],
    },
  ],
};

const schema = yup.object().shape({
  S3Bucket: yup
    .array()
    .of(
      yup.object().shape({
        bucket_name: yup.string().required().label('Bucket Name'),
        objects: yup.array().of(
          yup.object().shape({
            object_path: yup.string().required().label('Obj Path'),
          })
        ),
      })
    )
    .strict(),
});

function handleRemoveInstance(
  callback: (index: number) => void,
  index: number
) {
  callback(index);
}

function handleAddInstance(
  callback: (instanceType: typeof INSTANCE_DATA) => void,
  instanceType: typeof INSTANCE_DATA
) {
  callback(instanceType);
}

function onSubmit(values: any) {
  emits('updateStep');
  console.log(JSON.stringify(values, null, 2));
}
</script>
