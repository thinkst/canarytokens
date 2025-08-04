import { reactive, toRefs } from 'vue';

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
