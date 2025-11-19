<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div
    class="w-full justify-between items-center px-8 py-4 flex fixed top-0 bg-transparent z-100 bg-linear-to-b from-gray-400 via-30% to-transparent overflow-hidden"
  >
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1 class="text-[1.5rem] text-white hover:text-sky-300 transition-colors duration-300">
        Registro de sitios históricos
      </h1>
    </RouterLink>
    <div class="relative right-2 w-[40%]">
      <input
        type="text"
        class="flex w-full rounded-full background-transparent border border-[rgba(255,255,255,0.5)] focus:border-white focus:bg-[rgba(255,255,255,0.3)] focus:outline-none transition-background duration-300 text-white px-4 py-1 pr-31"
      />
      <select
        class="absolute top-1/2 right-0 -translate-y-1/2 text-gray-600 bg-white outline-none border-none appearance-none pr-6 pl-3 py-1 rounded-r-full"
      >
        <option value="name" selected>Nombre</option>
        <option value="province">Provincia</option>
        <option value="city">Ciudad</option>
      </select>
    </div>
    <nav class="flex items-center">
      <RouterLink
        to="/sitios"
        class="rounded-lg bg-sky-900 px-6 py-3 text-white text-lg hover:scale-105 transition-scale duration-300"
      >
        Sitios históricos
      </RouterLink>
      <RouterLink
        to="/login"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
        >Iniciar sesión</RouterLink
      >
    </nav>
  </div>
</template>

<style scoped></style>
