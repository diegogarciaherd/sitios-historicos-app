<script setup>
import { ref } from 'vue'
import SiteGrid from '@/components/SiteGrid.vue'
import SiteFilters from '@/components/SiteFilters.vue'

const filters = ref({})

function handleSearch(newFilters) {
  filters.value = newFilters
}
</script>

<template>
  <div class="h-screen bg-gray-50 overflow-hidden flex flex-col">
    <div class="flex-shrink-0 py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">
          Listado Sitios Históricos
        </h1>

        <!-- Layout: Mobile (stacked) / Desktop (sidebar + content) -->
        <div class="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)] lg:h-[calc(100vh-10rem)]">
          <!-- Filtros: Acordeón en móvil, Sidebar en desktop -->
          <aside class="w-full lg:w-80 flex-shrink-0 lg:overflow-y-auto">
            <SiteFilters v-model="filters" @search="handleSearch" />
          </aside>

          <!-- Contenido principal: Grid de sitios -->
          <main class="flex-1 min-w-0 overflow-y-auto">
            <SiteGrid :filters="filters" />
          </main>
        </div>
      </div>
    </div>
  </div>
</template>
