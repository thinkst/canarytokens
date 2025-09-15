import { reactive, toRefs } from 'vue';

// AI quota value defined in settings.py as AWS_INFRA_NAME_GENERATION_LIMIT
export const INITIAL_AI_QUOTA = 50;

const AIQuotaState = reactive({
  totalAiQuota: 0,
  availableAiQuota: 0,
  aiQuotaErrorShown: false,
  isTotalQuotaInitialized: false,
  isAvailableQuotaInitialized: false,
});


export function setTotalAIQuota(total: number) {
  AIQuotaState.isTotalQuotaInitialized = true;
  AIQuotaState.totalAiQuota = total;
}

export function setInitialAvailableAIQuota(available: number) {
  AIQuotaState.isAvailableQuotaInitialized = true;
  AIQuotaState.availableAiQuota = available;
}


// We need to set the initial available quota once after the first /generate-asset API response
// to show in the UI a meaningful starting quota after the plan loads.

export function updateAvailableAIQuota(available: number) {
  if (!AIQuotaState.isAvailableQuotaInitialized) {
    setInitialAvailableAIQuota(available);
    return;
  }

  // If the new value is smaller, update the quota.
  if (available < AIQuotaState.availableAiQuota) {
    AIQuotaState.availableAiQuota = available;
  }
}

export function getAIQuotaState() {
  return toRefs(AIQuotaState);
}

export function setAIQuotaErrorShown(shown: boolean) {
  AIQuotaState.aiQuotaErrorShown = shown;
}
