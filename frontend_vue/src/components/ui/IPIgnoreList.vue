<template>
    <Form class="flex flex-col gap-8" :validation-schema="ipListSchema" @submit="onSubmit">
      <Field v-slot="{ field, errorMessage }" name="ipAddresses">
        <textarea
          id="ip-ignore-list"
          v-bind="field"
          @input="(e) => { field.onInput(e); isSaved = false }"
          placeholder="Enter IP addresses separated by commas, spaces, semicolons, or new lines&#10;192.168.1.1, 10.0.0.1; 172.16.0.1&#10;203.0.113.0 198.51.100.0"
          rows="8"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
        />
        <p v-if="errorMessage" class="text-xs leading-4 text-red">
          {{ errorMessage }}
        </p>
      </Field>
      <BaseButton v-if="!isSaved" class="self-end" variant="primary" type="submit" :loading="isLoading">
        Save
      </BaseButton>
    </Form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as Yup from 'yup';
import type { NullableCanaryDropType } from '../tokens/types';
import { Form, Field, type GenericObject } from 'vee-validate';
import { getIPIgnoreList, updateIPIgnoreList, type UpdateIPIgnoreListType} from '@/api/main';

const props = defineProps<{
  canaryDrop: NullableCanaryDropType;
}>();

const isLoading = ref(false);
const isError = ref(false);
const isSaved = ref(true);
const errorMessage = ref('');
const initIpIgnoreList = ref('')

const ipv4Regex =
  /^(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/

const ipListSchema = Yup.object({
  ipAddresses: Yup.array()
      .transform((_, originalValue: string) => {
      if (!originalValue?.trim()) return []

      return originalValue
        .split(/[\s,;\n\r]+/)
        .map(ip => ip.trim())
        .filter(ip => ip.length > 0)
    })
    .max(100, 'You can ignore at most 100 IP addresses.')
    .of(
      Yup.string().matches(ipv4Regex, 'Must use valid IPv4 addresses.')
    )
})

onMounted(async () => {
  const savedIPs = await fetchSavedIPIgnoreList();
  if (savedIPs.length > 0) {
    initIpIgnoreList.value = savedIPs.join('\n');
  }
});

async function fetchSavedIPIgnoreList() {
  try {
  const res  = await getIPIgnoreList({
    token: props.canaryDrop!.canarytoken._value,
    auth: props.canaryDrop!.auth,
  });
  if (res.status === 200 && res.data.ip_ignore_list) {
    return res.data.ip_ignore_list;
  } else if (res.status !== 200) {
    isError.value = true;
    errorMessage.value = "Unable to fetch IP ignore list. Reload the page.";
  }

} catch (err) {
    isError.value = true;
    errorMessage.value = "Unable to fetch IP ignore list. Reload the page.";
}

  return [];
}

async function onSubmit(ipListValues: GenericObject) {
  isLoading.value = true;
  isError.value = false;
  try {
    const res = await updateIPIgnoreList(
      {
        token: props.canaryDrop!.canarytoken._value,
        auth: props.canaryDrop!.auth,
        ip_ignore_list: ipListValues.ipAddresses,
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
