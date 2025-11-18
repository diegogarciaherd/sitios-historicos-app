<script setup>
import SiteGrid from '@/components/SiteGrid.vue'
import SiteFilters from '@/components/SiteFilters.vue'
import Topbar from '@/components/Topbar.vue'
import SearchBar from '@/components/SearchBar.vue'
import MapSelector from '@/components/MapSelector.vue'
import { useSiteSearch } from '@/composables/useSiteSearch'

const {
  page,
  searchTerm,
  searchBarRef,
  siteFiltersRef,
  appliedFilters,
  combinedFilters,
  handleSearch,
  handleClear,
  handlePageChange
} = useSiteSearch()
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex flex-col">
    <Topbar />

    <div class="flex-1 flex flex-col gap-4 pt-20 sm:pt-24 lg:pt-28 px-4 sm:px-6 lg:px-8 pb-4">
      <div class="max-w-7xl mx-auto w-full flex flex-col gap-4">

        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900">
          Listado Sitios Históricos
        </h1>

        <!-- FILA SUPERIOR: filters + search -->
        <div class="flex flex-col lg:flex-row gap-4">

          <!-- Izquierda: Filtros + Mapa -->
          <aside class="w-full lg:w-80 flex flex-col gap-4">
            <SiteFilters 
              ref="siteFiltersRef"
              :applied-filters="appliedFilters"
              @clear="handleClear"
            />

            <MapSelector @nearby-sites="sites = $event" />
          </aside>

          <!-- Derecha: SearchBar + Grid -->
          <div class="flex-1 flex flex-col gap-4">
            <SearchBar 
              ref="searchBarRef"
              v-model="searchTerm"
              @search="handleSearch" 
            />

            <SiteGrid
              :siteFilters="combinedFilters"
              :page="page"
              @change-page="handlePageChange"
            />
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
