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
  <BaseFormSelect
    id="sql_server_sql_action"
    label="Select Server action"
    :options="sqlActions"
    required
    full-width
    placeholder="Choose an action"
    @select-option="handleSelectOption"
  />
  <!-- ...if NOT SELECT  -->
  <div
    v-if="selectedOption !== ''"
    class="flex flex-col gap-8 p-24 mb-8 text-center bg-white rounded-xl"
  >
    <span>On:</span>
    <!-- ...if NOT SELECT  -->
    <BaseFormTextField
      v-if="selectedOption !== 'SELECT'"
      id="sql_server_table_name"
      type="text"
      placeholder="e.g. TABLE1"
      label="Table name"
      full-width
    />
    <!-- ...if SELECT -->
    <BaseFormTextField
      v-if="selectedOption === 'SELECT'"
      id="sql_server_view_name"
      type="text"
      placeholder="e.g. VIEW1"
      label="Name SQL Server view"
      full-width
    />
    <font-awesome-icon
      class="text-sm font-semibold text-green-500"
      icon="arrow-down"
      aria-hidden="true"
    />
    <span>Fires:</span>
    <!-- ...if NOT SELECT  -->
    <BaseFormTextField
      v-if="selectedOption !== 'SELECT'"
      id="sql_server_trigger_name"
      type="text"
      placeholder="e.g. TRIGGER1"
      label="Name SQL Server trigger"
      full-width
    />
    <!-- ...if SELECT -->
    <BaseFormTextField
      v-if="selectedOption === 'SELECT'"
      id="sql_server_function_name"
      type="text"
      placeholder="e.g. FUNCTION1"
      label="Name SQL Server function"
      full-width
    />
  </div>
  <BaseFormTextField
    id="memo"
    label="Add Note"
    multiline
    required
    full-width
    helper-message="Reminder note when this token is triggered. For instance: SELECT SQL Server token on SQL01/CreditCards "
  ></BaseFormTextField>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const selectedOption = ref('');

const sqlActions = ['INSERT', 'DELETE', 'UPDATE', 'SELECT'];

function handleSelectOption(option: string) {
  selectedOption.value = option;
}
</script>
