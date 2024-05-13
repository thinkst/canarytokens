<!-- Skeleton loader as Fallback for ModalContentGenerateToken-->
<template>
  <div class="flex flex-col items-center w-full px-32">
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
      class="w-[50%] mt-16 mb-16"
    />
    <BaseSkeletonLoader
      class="w-full h-[10svh] md:w-[90%] lg:w-[70%] mb-8"
      type="rectangle"
    />
    <div class="flex flex-row gap-16">
      <BaseSkeletonLoader
        type="circle"
        class="w-[1.8rem] h-[1.8rem] mt-8"
      />
      <BaseSkeletonLoader
        type="circle"
        class="w-[1.8rem] h-[1.8rem] mt-8"
      />
      <BaseSkeletonLoader
        type="circle"
        class="w-[1.8rem] h-[1.8rem] mt-8"
      />
    </div>
    <BaseSkeletonLoader
      class="w-full md:w-[90%] lg:w-[70%] h-[300px] my-32"
      type="rectangle"
    />
  </div>
</template>

<script setup lang="ts"></script>
