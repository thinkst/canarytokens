<template>
  <div>
    <h3 class="inline-block mb-8 text-grey-500">Your Memo for this token</h3>
    <div
      class="flex flex-row items-center self-start flex-grow gap-16 py-8 w-full bg-grey-100 rounded-2xl min-h-[3rem] text-grey"
    >
      <font-awesome-icon
        icon="quote-left"
        class="pl-16 text-2xl text-grey-300"
      />
      <p class="py-8 text-pretty">
        <slot />
      </p>
    </div>
  </div>
</template>
