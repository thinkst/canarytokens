<template>
  <base-text-field
    id="email"
    type="text"
    placeholder="Url"
    label="Email or webhook URL"
    full-width
    helper-message="Provide an email address or webhook URL, or both space separated"
  />
  <base-text-field
    id="memo"
    label="Add Note"
    multiline
    full-width
  ></base-text-field>
</template>

<script setup lang="ts"></script>
