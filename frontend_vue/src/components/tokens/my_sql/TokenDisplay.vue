<template>
  <p class="mt-16 mb-16">1. Insert it into a MySQL dump of your own:</p>
  <base-code-snippet
    lang="javascript"
    label="Your MYSQL code"
    :code="tokenData.code"
  ></base-code-snippet>
  <p class="mt-32">
    2. Download a (pseudo) random MySQL dump with a token already embedded in it
  </p>
  <base-button
    class="mt-16"
    @click="handleDownloadDumpFile"
    >Download a MySQL Dump file</base-button
  >
  <base-switch
    id="encoded_mysql"
    v-model="encoded"
    class="mt-16"
    label="Encode Snippet"
  ></base-switch>
  <p class="text-sm">Encode snippet to make it harder to spot</p>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { downloadToken } from '@/api/main';
import { MySQLtokenDataType } from './types';

const props = defineProps<{
  tokenData: MySQLtokenDataType;
}>();

const encoded = ref(false);

function handleDownloadDumpFile() {
  console.log('download!');
  const params = {
    fmt: 'my_sql',
    auth: props.tokenData.auth,
    token: props.tokenData.token,
    encoded: encoded.value,
  };
  downloadToken(params)
    .then((res) => {
      window.location.href = res.request.responseURL;
    })
    .catch((err) => {
      console.log(err, 'err');
    })
    .finally(() => {
      console.log('You downloaded the file, yay!');
    });
}
</script>
