<template>
  <BaseFormTextField
    id="email"
    type="text"
    placeholder="Email"
    label="Email"
    full-width
    helper-message="Provide an email address or a webhook URL"
  />
  <BaseFormTextField
    id="url"
    type="text"
    placeholder="Webhook URL"
    label="Webhook URL"
    full-width
    helper-message="Provide an email address or a webhook URL"
  />
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    required
    full-width
  ></BaseFormTextField>
</template>

<script setup lang="ts"></script>
