import { reactive, toRefs } from 'vue';

const AIQuotaState = reactive({
  totalAiQuota: 0,
  availableAiQuota: 0,
  aiQuotaErrorShown: false,
});

export function setTotalAiQuota(total: number) {
  AIQuotaState.totalAiQuota = total;
}

export function setAvailableAiQuota(available: number) {
  AIQuotaState.availableAiQuota = available;
}

export function getAIQuotaState() {
  return toRefs(AIQuotaState);
}

export function setAiQuotaErrorShown(shown: boolean) {
  AIQuotaState.aiQuotaErrorShown = shown;
}
