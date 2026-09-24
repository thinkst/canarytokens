<template>
  <base-code-snippet
    lang="javascript"
    label="M365 account:"
    :code="account"
  ></base-code-snippet>
  <onepassword-save-button
    data-onepassword-type="login"
    :value="b64value"
    lang="en"></onepassword-save-button>
</template>

<script setup lang="ts">
import "@1password/save-button";
import { ref } from 'vue';

type OPDataType = {
  email_addr: string;
};

const props = defineProps<{
  tokenData: OPDataType;
}>();
const account = `Username: ${props.tokenData.email_addr}\nPassword: ${Math.random().toString(36).substr(2, 14)}`;
const data = {
  title: "M365 account",
  fields: [
    {
      autocomplete: "username",
      value: props.tokenData.email_addr
    },
    {
      autocomplete: "current-password",
      value: Math.random().toString(36).substr(2, 14)
    }
  ],
  notes: "Recovery account for Sharepoint, Outlook, Azure, and Entra ID (https://login.microsoftonline.com)"
};

const b64value = btoa(JSON.stringify(data));
</script>
