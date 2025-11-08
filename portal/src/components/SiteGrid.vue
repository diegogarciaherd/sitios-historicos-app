<script setup>
import { ref, computed, watch } from 'vue'
import DetailedSiteCard from './DetailedSiteCard.vue'

const props = defineProps({
  sites: { type: Array, default: () => [] },
  cols: { type: Number, default: 3, validator: (v) => v > 0 },
  rows: { type: Number, default: 2, validator: (v) => v > 0 },
  page: { type: Number, default: 1 },
})

const emit = defineEmits(['update:page'])

const internalPage = ref(props.page ?? 1)

const sitesList = computed(() => (Array.isArray(props.sites) ? props.sites : []))
const pageSize = computed(() => Math.max(1, (props.cols || 1) * (props.rows || 1)))
const pageCount = computed(() =>
  Math.max(1, Math.ceil((sitesList.value.length || 0) / pageSize.value) || 1),
)

function clampPage(p) {
  const n = Number(p) || 1
  if (n < 1) return 1
  if (n > pageCount.value) return pageCount.value
  return n
}

function setPage(p) {
  const c = clampPage(p)
  if (c !== internalPage.value) {
    internalPage.value = c
    emit('update:page', c)
  }
}

watch(
  () => props.page,
  (val) => {
    if (typeof val === 'number') setPage(val)
  },
)

watch([sitesList, pageSize], () => {
  if (internalPage.value > pageCount.value) setPage(pageCount.value)
})

const startIndex = computed(() => (internalPage.value - 1) * pageSize.value)
const endIndex = computed(() => startIndex.value + pageSize.value)
const visibleSites = computed(() => sitesList.value.slice(startIndex.value, endIndex.value))

const gotoPrev = () => setPage(internalPage.value - 1)
const gotoNext = () => setPage(internalPage.value + 1)

const gridTemplate = computed(() => `repeat(${props.cols || 1}, minmax(0, 1fr))`)

const liveMessage = computed(() => `Página ${internalPage.value} de ${pageCount.value}`)
</script>

<template>
  <section class="w-full" aria-label="Grilla de sitios con paginación">
    <!-- Controles superiores -->
    <div class="flex items-center justify-between mb-4">
      <div class="text-sm text-gray-600" aria-live="polite">{{ liveMessage }}</div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1 rounded bg-gray-800 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
          :disabled="internalPage === 1"
          @click="gotoPrev"
          aria-label="Página anterior"
        >
          Anterior
        </button>
        <button
          type="button"
          class="px-3 py-1 rounded bg-gray-800 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
          :disabled="internalPage === pageCount"
          @click="gotoNext"
          aria-label="Página siguiente"
        >
          Siguiente
        </button>
      </div>
    </div>

    <!-- Grid -->
    <div
      v-if="visibleSites.length"
      class="grid gap-6"
      :style="{ gridTemplateColumns: gridTemplate }"
      role="list"
      aria-label="Página actual"
    >
      <div
        v-for="(site, idx) in visibleSites"
        :key="startIndex + idx"
        role="listitem"
        class="flex justify-center"
      >
        <DetailedSiteCard
          :site="site"
          @click="$router.push(`/sites/${site.id || ''}`)"
          style="cursor: pointer"
        />
      </div>
    </div>
    <div v-else class="text-center text-gray-500 py-16">No hay sitios para mostrar.</div>

    <!-- Indicadores de páginas -->
    <div class="mt-4 flex items-center justify-center gap-2" role="tablist" aria-label="Paginación">
      <button
        v-for="p in pageCount"
        :key="p"
        type="button"
        class="w-8 h-8 rounded-full flex items-center justify-center text-sm border border-gray-400"
        :class="
          p === internalPage
            ? 'bg-gray-800 text-white border-gray-800'
            : 'bg-white text-gray-700 hover:bg-gray-100'
        "
        @click="setPage(p)"
        :aria-current="p === internalPage ? 'page' : undefined"
        :aria-label="`Ir a la página ${p}`"
      >
        {{ p }}
      </button>
    </div>
  </section>
</template>

<style scoped></style>
