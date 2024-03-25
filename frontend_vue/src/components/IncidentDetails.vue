<template>
  <div class="relative p-16 pb-32 m-4 bg-white rounded-md">
    <button
      type="button"
      class="absolute top-[10px] right-[20px]"
      @click="emit('update:modelValue', false)"
    >
      <font-awesome-icon
        icon="xmark"
        class="w-6 h-6 text-grey-400 hover:text-grey-200"
      />
    </button>
    <section class="p-16 mt-32 text-white rounded-md bg-red">
      <h2 class="font-semibold">Incident info</h2>
      <ul class="flex flex-col justify-between gap-24 mt-16 md:flex-row">
        <li class="flex flex-col gap-2">
          <span class="text-xs text-red-100">Date</span>
          <span class="font-semibold">2024-03-22 16:01:08.976860 </span>
        </li>
        <li class="flex flex-col gap-2">
          <span class="text-xs text-red-100">IP</span>
          <span class="font-semibold">84.138.198.174</span>
        </li>
        <li class="flex flex-col gap-2">
          <span class="text-xs text-red-100">Channel</span>
          <span class="font-semibold">HTTP</span>
        </li>
      </ul>
    </section>
    <section class="grid md:grid-cols-[auto_1fr] gap-32 mt-32 pl-8">
      <h3 class="text-grey-500">Geo coordinates</h3>
      <ul class="flex flex-col gap-16 pb-16 border-b md:ml-32 border-grey-100">
        <li>
          <span class="block text-xs uppercase text-grey-500">City</span>
          <span>Berlin </span>
        </li>
        <li>
          <span class="block text-xs uppercase text-grey-500"
            >Organisation</span
          >
          <span>AS3320 Deutsche Telekom AG</span>
        </li>
      </ul>
      <h3 class="text-grey-500">Basic info</h3>
      <ul class="flex flex-col gap-16 pb-16-b md:ml-32">
        <li>
          <span class="block text-xs uppercase text-grey-500">User Agent</span>
          <p>
            Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
          </p>
        </li>
        <li>
          <span class="block text-xs uppercase text-grey-500"
            >request headers</span
          >
          <code>
            {'Host': 'canarytokens.com', 'X-Real-Ip': '84.138.198.174',
            'X-Forwarded-For': '84.138.198.174', 'X-Forwarded-Host':
            'canarytokens.org', 'Connection': 'close',
            'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0
            (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like
            Gecko) Chrome/122.0.0.0 Safari/537.36', 'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate', 'Accept-Language':
            'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,it;q=0.5'}
          </code>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();
</script>

<style scoped>
ul {
  overflow: auto;
}

code {
  font-size: 0.8rem;
  line-height: 0.9rem;
  overflow-wrap: break-word;
}
</style>
