<!-- Skeleton loader as Fallback for ModalContentHotWoUse-->
<template>
  <div class="flex flex-col md:w-[100%] lg:w-[80%] sm:mt-40 px-8 w-full">
    <ul class="sm:grid sm:grid-cols-[1fr_1fr_1fr] flex flex-col">
      <li
        v-for="(item, i) in Array.from({ length: 3 })"
        :key="i"
        class="flex flex-row items-center flex-1 mt-16 sm:mt-0 sm:justify-start sm:flex-col"
      >
        <BaseSkeletonLoader
          class="h-[5rem] w-[5rem]"
          type="circle"
        />
        <div
          class="w-[80%] flex flex-col sm:items-center sm:ml-0 ml-24 sm:mt-16"
        >
          <BaseSkeletonLoader
            class="w-[80%]"
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
        </div>
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
