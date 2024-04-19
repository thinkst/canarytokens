<template>
  <TokenDisplay :token-data="tokenSnippetData" />
  <p class="mt-24 text-sm">
    Whenever someone tries to use this WireGuard VPN config to see what access
    it gets them, an alert is triggered.
  </p>
  <base-message-box
    class="mt-24"
    variant="info"
    message="This WireGuard config can be installed anywhere WireGuard is used, such as on phones, laptops and servers."
  />
  <p class="mt-24 text-center">Don't have the WireGuard app?</p>
  <div class="flex flex-row items-center justify-center gap-16 mt-16">
    <a
      href="https://apps.apple.com/us/app/wireguard/id1441195209?itsct=apps_box_badge&itscg=30200"
      target="_blank"
    >
      <img
        :src="getImageUrl('app-store.svg')"
        alt="Download form Apple store"
        class="h-[3rem]"
      />
    </a>
    <a
      href="https://play.google.com/store/apps/details?id=com.wireguard.android"
      target="_blank"
    >
      <img
        :src="getImageUrl('google-play.png')"
        alt="Download form Google Play store"
        class="h-[3rem]"
      />
    </a>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import type { NewTokenBackendType } from '@/components/tokens/types';
import TokenDisplay from './TokenDisplay.vue';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

const tokenSnippetData = ref({
  qr_code: props.tokenData.qr_code || '',
  wg_conf: props.tokenData.wg_conf || '',
});
</script>
