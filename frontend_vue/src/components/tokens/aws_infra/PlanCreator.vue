<template>
  <Form
    class="w-[80%] flex flex-col"
    :initial-values="initialValues"
    :validation-schema="schema"
    @submit="onSubmit"
  >
    <FieldArray
      v-slot="{ fields: buckets, push: pushBucket, remove: removeBucket }"
      name="S3Bucket"
    >
      <div class="flex justify-between items-center mb-16">
        <h3 class="font-bold">S3 Buckets</h3>
        <BaseButton
          icon="plus"
          @click="
            handleAddInstance(pushBucket, INSTANCE_DATA[INSTANCE_TYPE.S3BUCKET])
          "
          >New Bucket</BaseButton
        >
      </div>
      <fieldset
        v-for="(bucket, index) in buckets"
        :key="bucket.key"
        class="border bg-white rounded-2xl top-[0px] shadow-solid-shadow-grey border-grey-200 duration-100 ease-in-out justify-between token-card items-center p-24 mb-24"
      >
        <div class="flex justify-between items-center mb-24">
          <legend class="text-md font-semibold text-grey-400">
            S3Bucket #{{ index + 1 }}
          </legend>
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
              :key="object.object_path"
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
import { Form, FieldArray } from 'vee-validate';
import PlanCreatorTextField from '@/components/tokens/aws_infra/PlanCreatorTextField.vue';
import * as yup from 'yup';

const INSTANCE_TYPE = {
  S3BUCKET: 'S3Bucket',
  S3BUCKET_OBJECT: 'object_path',
  //   SQSQUEUE: 'SQSQueue',
  //   SSMPARAMETER: 'SSMParameter',
  //   SECRETMANAGERSECRET: 'SecretsManagerSecret',
  //   DYNAMODBTABLE: 'DynamoDBTable',
} as const;

const INSTANCE_DATA = {
  [INSTANCE_TYPE.S3BUCKET]: {
    bucket_name: '',
    objects: [],
  },
  [INSTANCE_TYPE.S3BUCKET_OBJECT]: {
    object_path: '',
  },
  //   [INSTANCE_TYPE.SQSQUEUE]: {
  //     queue_name: '',
  //     message_count: null,
  //   },
  //   [INSTANCE_TYPE.SSMPARAMETER]: {
  //     ssm_parameter_name: '',
  //     ssm_parameter_value: '',
  //   },
  //   [INSTANCE_TYPE.SECRETMANAGERSECRET]: {
  //     secretsmanager_secret_name: '',
  //     secretsmanager_secret_value: '',
  //   },
  //   [INSTANCE_TYPE.DYNAMODBTABLE]: {
  //     dynamodb_name: '',
  //     dynamodb_partition_key: '',
  //     dynamodb_row_count: '',
  //   },
};

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

function handleRemoveInstance(callback: () => void, index: number) {
  callback(index);
}

function handleAddInstance(
  callback: () => void,
  instanceType: typeof INSTANCE_DATA
) {
  callback(instanceType);
}

function onSubmit(values) {
  console.log(JSON.stringify(values, null, 2));
}
</script>
