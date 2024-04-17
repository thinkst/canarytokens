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
  <div class="relative">
    <BaseFormTextField
      id="cmd_process"
      type="text"
      placeholder="File name"
      label="Name of the process to monitor"
      helper-message="Add a .exe exstension, e.g klist.exe"
      full-width
    />
  </div>
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    required
    full-width
    helper-message="Reminder note when this token is triggered. For instance: AWS keys placed on Jim's laptop"
  ></BaseFormTextField>
</template>

<script setup lang="ts"></script>
