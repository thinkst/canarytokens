<!-- Skeleton loader as Fallback for ModalContentActivatedToken-->

<template>
  <div class="flex flex-col items-center w-full px-32 mb-32">
    <BaseSkeletonLoader
      type="circle"
      class="w-[80px] h-[80px] mt-8"
    />
    <BaseSkeletonLoader
      type="header"
      class="w-[200px] mt-24"
    />
    <BaseSkeletonLoader
      type="text"
      class="w-[200px] mt-8"
    />
    <div class="flex flex-col w-full items-left">
      <BaseSkeletonLoader
        type="text"
        class="w-[200px] mt-32"
      />
      <BaseSkeletonLoader
        type="rectangle"
        class="w-full mt-8 h-[50px]"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-[200px] mt-16"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-full mt-16"
      />
      <BaseSkeletonLoader
        type="rectangle"
        class="w-full h-[150px] mt-16"
      />
    </div>
  </div>
</template>

<script setup lang="ts"></script>
