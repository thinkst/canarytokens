import { ref } from 'vue';

export function useCountdown(initialValue) {
  const countdownSeconds = ref(initialValue);

  async function triggerCountdown() {
    return new Promise((resolve) => {
      const countdownTimer = setInterval(() => {
        countdownSeconds.value--;

        if (countdownSeconds.value <= 0) {
          clearInterval(countdownTimer);
          resolve(true);
        }
      }, 1000);
    });
  }

  return {
    countdownSeconds,
    triggerCountdown,
  };
}
