<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div
    class="w-full justify-between items-center px-8 py-4 flex fixed top-0 bg-transparent z-100 bg-linear-to-b from-gray-400 via-30% to-transparent"
  >
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1 class="text-[1.5rem] text-white hover:text-sky-300 transition-colors duration-300">
        Registro de sitios históricos
      </h1>
    </RouterLink>
    
    <nav>
      <RouterLink
        to="/about"
        class="text-white text-lg hover:text-sky-300 transition-colors duration-300"
        >Acerca de</RouterLink
      >
      <RouterLink
        to="/contact"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
        >Contacto</RouterLink
      >
      <RouterLink
        to="/login"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
        >Iniciar sesión</RouterLink
      >
    </nav>
  </div>
</template>

<style scoped></style>
