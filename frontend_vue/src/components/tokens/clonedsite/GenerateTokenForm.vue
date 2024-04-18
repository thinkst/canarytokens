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
    id="clonedsite"
    type="text"
    placeholder="e.g. thinkst.com"
    label="Domain of protected website"
    full-width
  />
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    required
    full-width
    helper-message="Reminder note when this token is triggered. For instance: Cloned website token for https://thinkst.com"
  />
</template>

<script setup lang="ts"></script>
