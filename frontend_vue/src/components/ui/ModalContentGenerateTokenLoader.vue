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
      class="w-[200px] mt-8"
    />
    <div class="flex flex-col w-full gap-8 md:w-[80%] lg:w-[60%] mt-32">
      <BaseSkeletonLoader
        type="text"
        class="w-[200px]"
      />
      <BaseSkeletonLoader
        type="header"
        class="w-full"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-[200px] mt-24"
      />
      <BaseSkeletonLoader
        type="header"
        class="w-full"
      />
      <BaseSkeletonLoader
        type="text"
        class="w-[200px] mt-24"
      />
      <BaseSkeletonLoader
        type="rectangle"
        class="w-full h-[150px]"
      />
    </div>
  </div>
</template>

<script setup lang="ts"></script>
