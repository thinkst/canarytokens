<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="text-center">
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
  </BaseGenerateTokenSettings>

  <GenerateTokenSettingsNotifications
    memo-helper-example="SELECT SQL Server token on SQL01/CreditCards"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';

const errorSqlServer = ref('');
const selectedValue = ref('');

const handleSelectedValue = (value: string) => {
  selectedValue.value = value;
};
</script>
