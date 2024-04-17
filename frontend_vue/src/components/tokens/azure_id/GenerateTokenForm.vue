<template>
  <BaseFormTextField
    id="email"
    type="text"
    placeholder="Email"
    label="Email"
    full-width
    helper-message="Provide an email address or webhook URL"
  />
  <BaseFormTextField
    id="webhook_url"
    type="text"
    placeholder="URL"
    label="URL"
    full-width
    helper-message="Provide an email address or webhook URL"
  />
  <BaseFormTextField
    id="azure_id_cert_file_name"
    type="text"
    placeholder="File Name"
    label="Azure ID certificate name"
    full-width
    helper-message="File Name of Azure ID certificate, like: Code_Sign_Server_3.pem"
  />
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    required
    full-width
    helper-message="Reminder note when this token is triggered. For instance: Azure Service Principal Login details on Code Sign Server 3"
  ></BaseFormTextField>
</template>

<script setup lang="ts"></script>
