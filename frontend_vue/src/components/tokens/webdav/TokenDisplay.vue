<template>
  <base-code-snippet
    lang="shell"
    label="Network Folder token"
    :code="snippetCode"
    custom-height="10rem"
    show-expand-button
  ></base-code-snippet>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import generateNetworkFoldertoken from './generateNetworkFolderToken';
import type { NetworkFolderDataType } from './types';

const props = defineProps<{
  tokenData: NetworkFolderDataType;
}>();

const NetworkFolder = ref({
  hostname: props.tokenData.hostname,
  webdav_fs_type: props.tokenData.webdav_fs_type,
  webdav_password: props.tokenData.webdav_password,
  webdav_server: props.tokenData.webdav_server,
});

const snippetCode = generateNetworkFoldertoken(NetworkFolder.value);
</script>
