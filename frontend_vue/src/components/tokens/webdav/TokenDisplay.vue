<template>
  <base-code-snippet
    lang="shell"
    label="On Windows systems, run these commands in cmd.exe:"
    :code="snippetWindowsCode"
    custom-height="6rem"
  ></base-code-snippet>
  <div>
    <label class="mt-16 mb-8 text-grey-500 inline-block" >On <strong>MacOS</strong> systems, configure a Network Folder with these steps:</label>
    <ul>
      <li>Open the Finder, then type &#8984;-K to Connect to Server</li>
      <li>Enter <strong>"{{NetworkFolder.webdav_server}}"</strong> as the hostname, and click Connect</li>
      <li>Enter any username (e.g. "user")</li>
      <li>Use <strong>{{NetworkFolder.webdav_password}}</strong> as the password</li>
      <li>Optionally you can save the credentials into your Keychain if you want to remount at login. To remount at log, open System Settings -> General -> Open at Login, click the \'+\' to add a new item, navigate to the newly-mounted folder, and select it, then click Open.</li>
    </ul>
  </div>
</template>

<style scoped>
ul {
  list-style-type: disc;
}

ul li {
  margin-left: 1em;
  padding-left: .3em;
  margin-bottom: 4px;
  border-radius: 4px;
}
</style>

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

const snippetWindowsCode = generateNetworkFoldertoken(NetworkFolder.value);
</script>
