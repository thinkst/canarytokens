<template>
  <BaseFormTextField
    id="email"
    type="text"
    placeholder="Url"
    label="Email or webhook URL"
    full-width
    helper-message="Provide an email address or webhook URL, or both space separated"
  />
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    full-width
  />
</template>

<script setup lang="ts"></script>
