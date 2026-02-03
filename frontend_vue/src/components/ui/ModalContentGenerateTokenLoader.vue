<!-- Skeleton loader as Fallback for ModalContentGenerateToken-->
<template>
  <div class="flex flex-col items-center w-full px-32">
    <BaseSkeletonLoader
      type="circle"
      class="w-[80px] h-[80px] mt-8"
    />
    <BaseSkeletonLoader
      class="w-full md:w-[90%] lg:w-[70%] h-[300px] my-32"
      type="rectangle"
    />
  </div>
</template>

<script setup lang="ts"></script>
