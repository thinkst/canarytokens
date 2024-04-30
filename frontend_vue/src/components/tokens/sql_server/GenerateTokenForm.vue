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
  <div
    class="px-16 py-24 text-center bg-white border rounded-3xl shadow-solid-shadow-grey border-grey-300"
  >
    <label
      for="radio-group-action"
      class="mb-4 ml-4 font-semibold"
      >Action</label
    >
    <div class="text-xs leading-0 text-red">{{ errorSqlServer }}</div>
    <div
      id="radio-group-action"
      class="flex flex-wrap gap-16 mt-8 mb-32 justify-evenly sm:flex-row"
    >
      <BaseRadioInput
        id="insert"
        value="INSERT"
        name="sql_server_sql_action"
        label="INSERT"
        @select-value="handleSelectedValue"
        @has-error="errorSqlServer = $event"
      />
      <BaseRadioInput
        id="update"
        value="UPDATE"
        name="sql_server_sql_action"
        label="UPDATE"
        @select-value="handleSelectedValue"
        @has-error="errorSqlServer = $event"
      />
      <BaseRadioInput
        id="delete"
        value="DELETE"
        name="sql_server_sql_action"
        label="DELETE"
        @select-value="handleSelectedValue"
        @has-error="errorSqlServer = $event"
      />
      <BaseRadioInput
        id="select"
        value="SELECT"
        name="sql_server_sql_action"
        label="SELECT"
        @select-value="handleSelectedValue"
        @has-error="errorSqlServer = $event"
      />
    </div>
    <BaseFormTextField
      v-if="selectedValue === 'SELECT'"
      id="sql_server_view_name"
      label="On this View"
      placeholder="YOUR_VIEW_NAME"
    />
    <BaseFormTextField
      v-else
      id="sql_server_table_name"
      label="On this Table"
      placeholder="YOUR_TABLE_NAME"
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

const errorSqlServer = ref('');
const selectedValue = ref('');

const handleSelectedValue = (value: string) => {
  selectedValue.value = value;
};
</script>
