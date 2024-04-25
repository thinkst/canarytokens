<!-- Skeleton loader as Fallback for ModalContentActivatedToken-->

<template>
  <div class="flex flex-col items-center w-full gap-16 px-32">
    <BaseSkeletonLoader
      type="circle"
      class="w-[100px] h-[100px]"
    />
    <BaseSkeletonLoader
      type="header"
      class="w-[200px]"
    />
    <BaseSkeletonLoader
      type="text"
      class="w-[200px]"
    />
    <BaseSkeletonLoader
      type="header"
      class="w-full"
    />
    <div class="flex flex-col w-full gap-8">
      <BaseSkeletonLoader
        type="text"
        class="w-[200px]"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-full"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-full"
      />
      <BaseSkeletonLoader
        type="rectangle"
        class="w-full h-[150px]"
      />
    </div>
  </div>
</template>

<script setup lang="ts"></script>
