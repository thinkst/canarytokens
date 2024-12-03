<template>
  <div>
    <label class="mt-16 mb-8 text-grey-500 inline-block" >Here are the generic parameters:</label>
    <div class="relative bg-white border rounded-2xl border-grey-100">
      <ul>
        <li>WebDAV server: <strong>{{NetworkFolder.webdav_server}}</strong><BaseCopyButton
              :content="webdavServer"
              class="ring-white ring-4 ml-8"
            /></li>
        <li>Username: Pick anything (e.g. <strong>service</strong>, <strong>Sabrina</strong>, or <strong>Admin</strong>)</li>
        <li>Password: <strong>{{NetworkFolder.webdav_password}}</strong><BaseCopyButton
              :content="webdavPassword"
              class="ring-white ring-4 ml-8"
            /></li>
      </ul>
    </div>
  </div>
  <label class="mt-16 mb-8 text-grey-500 inline-block" >On <strong>Windows</strong> systems, run these commands in cmd.exe:</label>
  <base-code-snippet
    lang="shell"
    :code="snippetWindowsCode"
    custom-height="9.5rem"
  ></base-code-snippet>
  <div>
    <label class="mt-16 mb-8 text-grey-500 inline-block" >On <strong>MacOS</strong> systems, configure a Network Folder with these steps:</label>
    <div class="relative bg-white border rounded-2xl border-grey-100 mr-2.5rem]">
      <ul>
        <li>Open the Finder, then type &#8984;-K to Connect to Server.</li>
        <li>Copy and paste <span id="input-wrapper">
            <input class="w-[12rem]" :value="webdavUrl" />
            <BaseCopyButton
              :content="webdavUrl"
              class="ring-white ring-4"
            />
          </span> as the hostname, then click Connect.</li>
        <li>Alternatively, to automatically mount the folder at login, use the "WebDAV server" field above as the hostname, then enter the username and password and check "Remember this password in my Keychain". Open System Settings -> General -> Open at Login, click the '+' to add a new item, navigate to the newly-mounted folder, and select it, then click Open.</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
ul {
  list-style-type: disc;
  padding: 1em;
}

ul li {
  margin-left: 1em;
  padding-left: .3em;
}

input {
  text-overflow:ellipsis;
}

#input-wrapper {
  outline: 2px solid hsl(162, 86%, 36%);
  padding: .6rem;
  font-family: monospace;
}

input:focus-visible {
  outline: none;
}
</style>

<script setup lang="ts">
import { ref } from 'vue';
import { generateNetworkFoldertoken, generateWebdavUrl } from './generateNetworkFolderToken';
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
const webdavUrl = generateWebdavUrl(NetworkFolder.value);
const webdavServer = NetworkFolder.value.webdav_server ? NetworkFolder.value.webdav_server : 'error';
const webdavPassword = NetworkFolder.value.webdav_password ? NetworkFolder.value.webdav_password : 'error';;
</script>
