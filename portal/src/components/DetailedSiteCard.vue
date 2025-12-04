<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSiteCoverImage } from '../api/sites'
import Tag from '@/components/Tag.vue'

const props = defineProps({
  site: {
    type: Object,
    required: true,
  },
  classes: {
    type: String,
    default: 'w-full aspect-4/5',
  },
})

const stateColors = {
  Bueno: 'badge-success',
  Regular: 'badge-warning',
  Malo: ' [--badge-color:red]',
}

const cover_image = ref('')

const averageRating = computed(() => {
  if (!props.site || !props.site.cantidadResenas) return 0
  const total = Number(props.site.puntuacionTotal) || 0
  const count = Number(props.site.cantidadResenas) || 0
  if (!count) return 0
  const avg = total / count
  if (!Number.isFinite(avg)) return 0
  return Math.min(5, Math.max(0, avg))
})

const ratingCount = computed(() => {
  if (!props.site) return 0
  const count = Number(props.site.cantidadResenas)
  return Number.isFinite(count) && count > 0 ? count : 0
})

const ratingStars = computed(() => {
  return Array.from({ length: 5 }, (_, index) => {
    const value = averageRating.value - index
    if (value >= 1) return 100
    if (value <= 0) return 0
    return Math.round(value * 100)
  })
})

const ratingAriaLabel = computed(() => {
  const count = ratingCount.value
  if (!count) return 'Sin reseñas registradas'
  const plural = count === 1 ? 'reseña' : 'reseñas'
  return `Puntuación promedio ${averageRating.value.toFixed(1)} de 5 basada en ${count} ${plural}`
})

const starPath =
  'M22,9.81a1,1,0,0,0-.83-.69l-5.7-.78L12.88,3.53a1,1,0,0,0-1.76,0L8.57,8.34l-5.7.78a1,1,0,0,0-.82.69,1,1,0,0,0,.28,1l4.09,3.73-1,5.24A1,1,0,0,0,6.88,20.9L12,18.38l5.12,2.52a1,1,0,0,0,.44.1,1,1,0,0,0,1-1.18l-1-5.24,4.09-3.73A1,1,0,0,0,22,9.81Z'
const starUid = Math.random().toString(36).slice(2, 8)

onMounted(async () => {
  try {
    const imageUrl = await getSiteCoverImage(props.site.id)
    cover_image.value = imageUrl
  } catch (error) {
    console.error('Error al cargar la imagen de portada:', error)
    cover_image.value = '' // Fallback en caso de error
  }
})
</script>

<template>
  <div
    :class="`site-card relative rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 ${classes} bg-slate-950`"
  >
    <img
      :src="cover_image"
      :alt="site.nombre"
      class="absolute inset-0 w-full h-full object-cover z-0"
    />

    <div class="mt-1 flex items-center gap-3 text-sm text-slate-300 absolute top-4 right-4 z-10">
      <div class="rating-stars" role="img" :aria-label="ratingAriaLabel" :title="ratingAriaLabel">
        <svg
          v-for="(fill, index) in ratingStars"
          :key="`star-${index}`"
          viewBox="0 0 24 24"
          class="rating-star"
        >
          <defs>
            <clipPath :id="`clip-star-${starUid}-${index}`">
              <path :d="starPath" />
            </clipPath>
          </defs>
          <rect
            width="24"
            height="24"
            fill="rgba(148, 163, 184, 0.3)"
            :clip-path="`url(#clip-star-${starUid}-${index})`"
          />
          <rect
            :width="(fill / 100) * 24"
            height="24"
            fill="#facc15"
            :clip-path="`url(#clip-star-${starUid}-${index})`"
          />
          <path
            :d="starPath"
            fill="none"
            stroke="#facc15"
            stroke-width="1.2"
            stroke-linejoin="round"
          />
        </svg>
      </div>
    </div>

    <div
      class="absolute bottom-0 p-4 text-start text-white bg-linear-to-t from-gray-800 to-transparent w-full z-10"
    >
      <h2 class="text-large font-semibold mb-2">{{ site.nombre }}</h2>
      <p class="mb-2 text-sm">{{ site.descripcionBreve }}</p>
      <p class="mb-2 text-sm">{{ site.ciudad }} | {{ site.provincia }}</p>

      <span class="badge badge-dash badge-primary" :class="stateColors[site.estado] || 'badge'">
        {{ site.estado }}
      </span>

      <div class="flex mt-2 space-2 flex-wrap max-h-14 items-end">
        <Tag
          v-for="(tag, index) in site.tags.slice(0, 5)"
          :key="tag.id || index"
          :tag="tag"
          :selected-tags="[]"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.rating-star {
  width: 0.9rem;
  height: 0.9rem;
}

.rating-star rect {
  transition: width 200ms ease;
}
</style>
