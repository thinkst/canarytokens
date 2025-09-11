import { reactive, toRefs } from 'vue';

// AI quota value defined in settings.py as AWS_INFRA_NAME_GENERATION_LIMIT
export const INITIAL_AI_QUOTA = 50;

const AIQuotaState = reactive({
  totalAiQuota: 0,
  availableAiQuota: 0,
  aiQuotaErrorShown: false,
});

export function setTotalAIQuota(total: number) {
  AIQuotaState.totalAiQuota = total;
}

export function setAvailableAIQuota(available: number) {
    AIQuotaState.availableAiQuota = available;
}

export function getAIQuotaState() {
  return toRefs(AIQuotaState);
}

export function setAIQuotaErrorShown(shown: boolean) {
  AIQuotaState.aiQuotaErrorShown = shown;
}
