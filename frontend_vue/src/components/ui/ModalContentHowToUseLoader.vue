<!-- Skeleton loader as Fallback for ModalContentHotWoUse-->
<template>
  <div class="flex flex-col md:w-[100%] lg:w-[80%] sm:mt-40 px-8">
    <ul class="sm:grid sm:grid-cols-[1fr_1fr_1fr] sm:gap-40 w-full">
      <li
        v-for="(item, i) in Array.from({ length: 3 })"
        :key="i"
        class="flex flex-row mt-16 sm:items-center sm:justify-start sm:flex-col sm:mt-0"
      >
        <BaseSkeletonLoader
          class="h-[5rem] w-[5rem]"
          type="circle"
        />
        <BaseSkeletonLoader
          class="w-[80%] mt-24"
          type="text"
        />
        <BaseSkeletonLoader
          class="w-full mt-8"
          type="text"
        />
        <BaseSkeletonLoader
          class="w-full mt-8"
          type="text"
        />
      </li>
    </ul>
    <BaseSkeletonLoader
      class="w-full mt-40"
      type="header"
    />
    <BaseSkeletonLoader
      class="w-full mt-16"
      type="header"
    />
    <BaseSkeletonLoader
      class="w-full mt-16"
      type="header"
    />
  </div>
</template>

<script setup lang="ts"></script>
