<template>
    <form class="flex flex-col gap-8" :validation-schema="ipListSchema" @submit="submit">
      <Field v-slot="{ field, errorMessage }" name="ipAddresses">
        <textarea
          id="ip-ignore-list"
          v-bind="field"
          class="px-16 py-8 relative bg-white border rounded-2xl border-grey-100"
          @input="(e) => { field.onInput(e); isSaved = false }"
          placeholder="Enter IP addresses separated by new lines&#10;192.168.1.1&#10;10.0.0.1&#10;172.16.0.1&#10;203.0.113.0&#10;198.51.100.0"
          rows="8"
        />
        <p v-if="errorMessage" class="text-xs leading-4 text-red">
          {{ errorMessage }}
        </p>
      </Field>
      <BaseButton v-if="!isSaved" class="self-end" variant="primary" type="submit" :loading="isLoading">
        Save
      </BaseButton>
    </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as Yup from 'yup';
import type { NullableCanaryDropType } from '../tokens/types';
import { Field, type GenericObject, useForm } from 'vee-validate';
import { updateIPIgnoreList, type UpdateIPIgnoreListType} from '@/api/main';

const props = defineProps<{
  canaryDrop: NullableCanaryDropType;
}>();

const isLoading = ref(false);
const isError = ref(false);
const isSaved = ref(true);
const errorMessage = ref('');

const ipv4Regex =
  /^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/

const ipListSchema = Yup.object({
  ipAddresses: Yup.array()
      .transform((_, originalValue: string) => {
      if (!originalValue?.trim()) return []

      return originalValue
        .split(/[\n]+/)
        .map(ip => ip.replace(/\s+/g, ''))
        .filter(ip => ip.length > 0)
    })
    .max(100, 'You can ignore at most 100 IP addresses.')
    .of(
      Yup.string().matches(ipv4Regex, 'Must use valid IPv4 addresses with a single IP address per line')
    )
});

const { resetForm, handleSubmit } = useForm({
  validationSchema: ipListSchema,
  initialValues: { ipAddresses: '' },
});

const submit = handleSubmit(onSubmit);

onMounted(async () => {
  const savedIPs = props.canaryDrop.alert_ignored_ips || [];
    if (savedIPs.length > 0) {
    resetForm({ values: { ipAddresses: savedIPs.join('\n') } });
  }
});


async function onSubmit(ipListValues: GenericObject) {
  isLoading.value = true;
  isError.value = false;
  try {
    const ipList = ipListSchema.cast(ipListValues).ipAddresses as string[];
    const res = await updateIPIgnoreList(
      {
        token: props.canaryDrop!.canarytoken._value,
        auth: props.canaryDrop!.auth,
        ip_ignore_list: ipList,
      } as UpdateIPIgnoreListType
    );

    if (res.status !== 200) {
      isError.value = true;
      errorMessage.value = "Unable to update IP ignore list.";
    }
  } catch (err: any) {
    isError.value = true;
    errorMessage.value = "Unable to update IP ignore list.";
    } finally {
    isLoading.value = false;
    isSaved.value = true;
  }
}

</script>

<style scoped>

</style>
