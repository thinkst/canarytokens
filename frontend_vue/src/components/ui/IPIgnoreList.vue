<!-- <template>
  <div class="settings-item">
    <div class="settings-item-actions">

      <div style="display: flex; justify-content: space-between;" class="header_container">

        <div class="flex">

          <BaseSwitch
            id="ip-ignorable-list"
            v-model="settingRefs.EMAIL"
            label="Email alerts"
            :helper-message="tokenBackendResponse.canarydrop.alert_email_recipient"
            :loading="loadingRefs.EMAIL"
            :has-error="errorRefs.EMAIL"
            :error-message="errorMessage"
            @click.prevent="
                handleChangeSetting(
                SETTINGS_TYPE.EMAIL as keyof typeof SETTINGS_TYPE,
                !settingRefs.EMAIL
        )
      "
          />

          <div class="text-right margin-left--8" v-if="!sectionSettings.enabled">
            <div>
              <transition
                name="fade"
                mode="out-in"
              >
                <div
                  class="enabled-state"
                  key="loading"
                  v-if="loading"
                >
                  <BaseLoadingSpinner class="margin-right--12" />
                </div>
                <div
                  class="enabled-state"
                  key="saved"
                  v-else-if="saved"
                >
                  <font-awesome-icon class="margin-right--12" icon="check" color="green" />
                </div>
                <div
                  class="enabled-state"
                  key="failed"
                  v-else-if="failed"
                >
                  <font-awesome-icon class="margin-right--12" icon="times" color="#dc3545" />
                </div>
              </transition>
            </div>
          </div>

        </div>
        <div>
          <base-what-is-this
            v-if="setting.id === 'snmp_whitelist'"
            link="https://help.canary.tools/hc/en-gb/articles/360002425937-So-long-SNMP-"
            margin="0"
            font-size="15px" />
          <base-what-is-this
            link="https://help.canary.tools/hc/en-gb/articles/360012758717-How-can-I-ignore-IPs-and-Ports-from-hitting-my-Canary-"
            margin="0"
            v-show="sectionSettings.enabled === true"
            font-size="15px" />
        </div>
      </div>

      <div class="settings-item-actions--save margin-top--8" v-if="sectionSettings.enabled">
        <div>
          <transition
            name="fade"
            mode="out-in"
          >
            <div
              class="enabled-state"
              key="loading"
              v-if="loading"
            >
              <BaseLoadingSpinner class="margin-right--12" />
            </div>
            <div
              class="enabled-state"
              key="saved"
              v-else-if="saved"
            >
              <font-awesome-icon class="margin-right--12" icon="check" color="green" />
            </div>
            <div
              class="enabled-state"
              key="failed"
              v-else-if="failed"
            >
              <font-awesome-icon class="margin-right--12" icon="times" color="#dc3545" />
            </div>
          </transition>
        </div>
      </div>
      <template v-if="setting.input">
        <template v-if="sectionSettings.enabled">
          <b-form-textarea
            class="ip-details"
            v-model="sectionSettings.details"
            :placeholder="setting.input_placeholder"
            rows=6>
          </b-form-textarea>
        </template>
      </template>
      <div
        v-if="sectionSettings.enabled"
        class="flex gap--8 margin-vertical--12 justify-content-end align-content-center">
        <div
          class="error margin-top--8 margin-right--12"
          v-if="failed"
        >{{ failed_reason }}</div>

        <div class="flex gap--8">
          <base-button
            @click="reset"
            v-show="sectionSettings.enabled"
            :disabled="!showSaveAndReset"
          >
            Reset
          </base-button>
          <base-button
            variant="success"
            @click="saveDetails(setting.id)"
            :disabled="v$.sectionSettings.details.$error"
            v-show="showSaveAndReset">
            Save
          </base-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

    const props = defineProps<{
        tokenBackendResponse: ManageTokenBackendType;
    }>();

</script>

<style scoped>

</style> -->
