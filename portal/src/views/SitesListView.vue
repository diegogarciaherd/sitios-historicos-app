<script setup>
import SiteGrid from '@/components/SiteGrid.vue'
import SiteFilters from '@/components/SiteFilters.vue'
import Topbar from '@/components/Topbar.vue'
import SearchBar from '@/components/SearchBar.vue'
import { useSiteSearch } from '@/composables/useSiteSearch'

const {
  searchBarRef,
  siteFiltersRef,
  combinedFilters,
  handleSearch,
  handleClear
} = useSiteSearch()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Topbar fijo en la parte superior -->
    <Topbar />
    
    <!-- Contenido principal con padding-top para no quedar debajo del Topbar -->
    <div class="flex-1 flex flex-col gap-4 pt-20 sm:pt-24 lg:pt-28 px-4 sm:px-6 lg:px-8 pb-4 sm:pb-6">
      <div class="max-w-7xl mx-auto w-full flex flex-col gap-4">
        
        <!-- Título -->
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">
          Listado Sitios Históricos
        </h1>
        
        <!-- Barra de búsqueda -->
        <div class="w-full">
          <SearchBar ref="searchBarRef" @search="handleSearch" />
        </div>

        <!-- Layout: Filtros y Grid -->
        <div class="flex flex-col lg:flex-row gap-4">
          <!-- Filtros: Acordeón en móvil, Sidebar en desktop -->
          <aside class="w-full lg:w-80 shrink-0">
            <SiteFilters 
              ref="siteFiltersRef"
              @clear="handleClear"
            />
          </aside>

          <!-- Contenido principal: Grid de sitios -->
          <main class="flex-1 min-w-0">
            <SiteGrid :site-filters="combinedFilters" />
          </main>
        </div>
      </div>
    </div>
  </div>
</template>
