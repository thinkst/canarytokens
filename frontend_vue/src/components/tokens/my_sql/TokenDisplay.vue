<template>
  <p class="mt-16 mb-16">1. Insert it into a MySQL dump of your own</p>
  <base-code-snippet
    lang="sql"
    label="Your MYSQL code"
    :code="codeMYSQL"
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
    helper-message="Encode snippet to make it harder to spot"
    @input.stop="handleEncodingChange()"
  ></base-switch>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { Ref } from 'vue';
import { downloadAsset } from '@/api/main';
import generateMysqlToken from '@/components/tokens/my_sql/generateMysqlToken';

type MySQLtokenDataType = {
  hostname: string;
  auth: string;
  token: string;
  encoded?: boolean;
};

const props = defineProps<{
  tokenData: MySQLtokenDataType;
}>();

const encoded: Ref<boolean> = ref(props.tokenData.encoded || true);
const codeMYSQL = ref('');

onMounted(() => {
  codeMYSQL.value = generateMysqlToken(
    props.tokenData.hostname,
    props.tokenData.token,
    encoded.value
  );
});

function handleEncodingChange() {
  encoded.value = !encoded.value;
  codeMYSQL.value = generateMysqlToken(
    props.tokenData.hostname,
    props.tokenData.token,
    encoded.value
  );
}

function handleDownloadDumpFile() {
  const params = {
    fmt: 'my_sql',
    auth: props.tokenData?.auth,
    token: props.tokenData?.token,
    encoded: encoded.value,
  };
  downloadAsset(params)
    .then((res) => {
      window.location.href = res.request.responseURL;
    })
    .catch((err) => {
      console.log(err, 'err');
    })
    .finally(() => {
      console.log('File downloaded');
    });
}
</script>
