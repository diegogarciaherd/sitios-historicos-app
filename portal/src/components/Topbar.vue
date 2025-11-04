<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="w-full justify-between items-center px-8 py-4 flex fixed top-0 bg-transparent z-10">
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1 class="text-[1.5rem] text-white">Registro de sitios históricos</h1>
    </RouterLink>
  </div>
</template>

<style scoped></style>
