<template>
  <div class="payments-portal-container">
    <div class="payments-portal flex items-center justify-center p-24 border border-grey-200 rounded-xl shadow-solid-shadow-grey relative">
      <button
        @click="emit('close')"
        class="close h-[2rem] w-[2rem] font-semibold text-white rounded-full bg-green hover:bg-green-300 transition duration-100"
        >
        <font-awesome-icon
          icon="times"
          aria-hidden="true"
          :class="loading && 'opacity-30'"
        />
      </button>

      <div v-if="currentState === _PaymentsFlowStates._Form" class="flex items-center justify-center w-full gap-4">
        <div class="form flex-col gap-[24px] w-[225px] sm:w-[325px]">
        <div class="flex-col">
          <p class="mb-[28px] p-[16px] mt-[24px] lg:mt-[12px]">
            We'll generate a fake transaction that'll trigger alert notifications for this token.
          </p>
          <label class="form-label">Card Number</label>
          <div style="position: relative">
            <input disabled :value="formatCreditCardNumber(props.tokenData.card_number)">
            <div class="visa credit-card">
              <img :src="getImageUrl(`icons/credit-card-token/visa.svg`)" />
            </div>
            <div class="mastercard credit-card">
              <img :src="getImageUrl(`icons/credit-card-token/mastercard.svg`)" />
            </div>
            <div class="canary credit-card">
              <img :src="getImageUrl(`icons/credit-card-token/canary.svg`)" />
            </div>
          </div>
        </div>

        <div class="flex gap-[24px]">
          <div class="flex-col form-col w-full">
            <label class="form-label">Expiration date</label>
            <input disabled :value="`${props.tokenData.expiry_month}/${props.tokenData.expiry_year}`">
          </div>
          <div class="flex-col form-col w-full">
            <label class="form-label">Security code</label>
            <input disabled :value="props.tokenData.cvv">
          </div>
        </div>
        <div v-if="error" class="error">Oops... Something went wrong!</div>
        <button type="button" @click="triggerDemoAlert" :class="{ loading: loading }" :disabled="loading">
          <BaseSpinner
            v-if="loading"
            height="1.5rem"
            variant="secondary"
            class="absolute left-0 right-0 ml-auto mr-auto"
          ></BaseSpinner>
          <span>Pay $100.00</span>
        </button>
        </div>
      </div>

      <div v-else-if="currentState === _PaymentsFlowStates._Done">
        <div class="text-center">
          <p class="payment-received-header">Payment received!</p>
          <p class="payment-received">You'll get a notification soon if you
          <RouterLink
            :to="`/history/${props.tokenData.auth}/${props.tokenData.token}`"
            class="text-green-600 hover:text-green-500 font-bold"
          >
           haven't already.
          </RouterLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import type { CreditCardDataType } from '@/components/tokens/credit_card_v2/CreditCardToken.vue';
  // @ts-ignore
  import confetti from 'canvas-confetti';
  import { triggerDemoCreditCardAlert } from '@/api/main';
  import getImageUrl from '@/utils/getImageUrl';

  const props = defineProps<{
    tokenData: CreditCardDataType,
  }>();

  const emit = defineEmits(['close']);

  enum _PaymentsFlowStates {
    _Form,
    _Done,
  }

  const currentState = ref(_PaymentsFlowStates._Form);
  const loading = ref(false);
  const error = ref(false);

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min;
  }

  function formatCreditCardNumber(number: string) {
    return `${number.match(/(\d{4})/g)?.join(' ')}`;
  }

  function addConfetti() {
    const confettiCanvas = document.createElement('canvas');
    const modal = document.querySelector('.payments-portal');
    modal?.appendChild(confettiCanvas);

    Object.assign(confettiCanvas.style, {
      position: 'absolute',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
    });

    Object.assign(confettiCanvas, {
      with: window.innerWidth,
      height: window.innerHeight,
    });

    const myConfetti = confetti.create(confettiCanvas, { resize: true });

    const duration = 25 * 1000;
    const animationEnd = Date.now() + duration;
    let skew = 2;
    const money = confetti.shapeFromText({ text: '💵', scalar: 1.5 });

    (function frame() {
      const timeLeft = animationEnd - Date.now();
      const ticks = Math.max(200, 500 * (timeLeft / duration));
      skew = Math.max(0.8, skew - 0.001);

      myConfetti({
        particleCount: 1,
        startVelocity: 0,
        ticks,
        origin: {
          x: Math.random() * 5,
          // since particles fall down, skew start toward the top
          y: (Math.random() * skew) - 0.2,
        },
        shapes: [money],
        gravity: randomInRange(0.2, 0.3),
        scalar: randomInRange(1.5, 1.5),
        drift: randomInRange(-0.4, 0.4),
      });

      if (timeLeft > 0) {
      requestAnimationFrame(frame);
      }
    }());
  }

  async function triggerDemoAlert() {
    error.value = false;
    try {
      loading.value = true;
      await triggerDemoCreditCardAlert(props.tokenData.card_id, props.tokenData.card_number);
      currentState.value = _PaymentsFlowStates._Done;
      addConfetti();
    } catch (err) {
      console.log(err);
      error.value = true;
    } finally {
      loading.value = false;
    }
  }
</script>

<style lang="scss" scoped>
  .payments-portal-container {
    @media (max-width: 992px)  {
      padding-right: 0px;
    }
  }

  .payments-portal {
    background-color: #fff;
    width: 100%;
    height: 100%;
    min-height: 400px;
  }

  .form {
    label {
      font-size: 12px;
      color: #0a2540;
    }

    input {
      border-radius: 4px;
      border: 1px solid #e6ebf1;
      box-shadow: rgba(0, 0, 0, 0.03) 0px 1px 1px 0px, rgba(18, 42, 66, 0.02) 0px 3px 6px 0px;
      font-size: 14px;
      line-height: 0;
      padding: 8px;
      padding-left: 8px;
      width: 100%;
    }

    button {
      width: 100%;
      font-weight: 700;
      border-radius: 4px;
      padding: 0 12px;
      height: 36px;
      color: white;
      background-color: #0a2540;
      margin-top: 8px;
      border: 0;
      position: relative;
    }

    .credit-card {
      width: 25px;
      height: 16px;
      position: absolute;
      border-radius: 3px;
      display: flex;
      align-items: center;
      justify-content: center;
      top: 10px;
    }

    .visa {
      right: 68px;
      border: 1px solid #e6ebf1;
      background-color: white;

      img {
        width: 25px;
        height: 16px;
      }
    }

    .mastercard {
      right: 38px;
      background-color: #252525;

      img {
        width: 25px;
        height: 16px;
      }
    }

    .canary {
      right: 8px;
      background-color: white;
      border: 1px solid #e6ebf1;

      img {
        width: 18px;
        height: 12px;
      }
    }

    p {
      font-weight: 500;
      font-size: 14px;
      color:  var(--dark-color);
      border: 1px solid #e6ebf1;
      padding: 12px;
      margin-bottom: 22;
      border-radius: 6px;
      box-shadow: rgba(0, 0, 0, 0.03) 0px 1px 1px 0px, rgba(18, 42, 66, 0.02) 0px 3px 6px 0px;
    }
  }

  .close {
    position: absolute !important;
    top: 8px;
    right: 8px;
  }

  .loading {
    opacity: 0.8;
  }

  .payment-received-header {
    color: var(--primary-color-code);
    font-weight: 700;
    margin-bottom: 8px;
  }

  .payment-received {
    font-weight: 500;
    font-size: 14px;
    color:  var(--dark-color);
  }

  .error {
    margin: 0;
    color: red;
    text-align: center;
  }

  .flex-col {
    display: flex;
    flex-direction: column;
  }

  .form-label {
    font-weight: 700;
    margin-bottom: 8px;
  }
</style>
