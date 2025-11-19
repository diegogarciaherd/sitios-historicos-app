<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => [], // [{ src, alt? }] or string
  },
  autoplay: { type: Boolean, default: false },
  interval: { type: Number, default: 5000 },
  loop: { type: Boolean, default: true },
  pauseOnHover: { type: Boolean, default: true },
  showThumbnails: { type: Boolean, default: true },
  showArrows: { type: Boolean, default: true },
  ariaLabel: { type: String, default: 'Galeria de imagenes del sitio' },
})

const emit = defineEmits(['change'])

const current = ref(0)
const hovering = ref(false)
let timerId = null

const count = computed(() => props.images.length)
const canNavigate = computed(() => count.value > 1)

function clampIndex(idx) {
  if (count.value === 0) return 0
  if (props.loop) return (idx + count.value) % count.value
  return Math.min(Math.max(idx, 0), count.value - 1)
}

function goTo(idx) {
  const next = clampIndex(idx)
  if (next !== current.value) {
    current.value = next
    emit('change', next)
  }
}

function next() {
  goTo(current.value + 1)
}

function prev() {
  goTo(current.value - 1)
}

function startAutoplay() {
  stopAutoplay()
  if (!props.autoplay || !canNavigate.value) return
  timerId = setInterval(() => {
    if (props.pauseOnHover && hovering.value) return
    next()
  }, props.interval)
}

function stopAutoplay() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

const touchStartX = ref(0)
const touchStartY = ref(0)
const touchActive = ref(false)

function onTouchStart(event) {
  if (!canNavigate.value) return
  const firstTouch = event.touches?.[0]
  if (!firstTouch) return
  touchActive.value = true
  touchStartX.value = firstTouch.clientX
  touchStartY.value = firstTouch.clientY
}

function onTouchEnd(event) {
  if (!touchActive.value) return
  touchActive.value = false
  const firstTouch = event.changedTouches?.[0]
  if (!firstTouch) return
  const dx = firstTouch.clientX - touchStartX.value
  const dy = firstTouch.clientY - touchStartY.value
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 36) {
    dx < 0 ? next() : prev()
  }
}

function onKeydown(event) {
  if (!canNavigate.value) return
  if (event.key === 'ArrowRight') {
    event.preventDefault()
    next()
  }
  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    prev()
  }
}

watch(() => props.autoplay, startAutoplay)
watch(() => props.interval, startAutoplay)
watch(count, (newCount) => {
  if (newCount === 0) {
    stopAutoplay()
    current.value = 0
    return
  }
  if (current.value >= newCount) {
    current.value = props.loop ? clampIndex(current.value) : newCount - 1
  }
  startAutoplay()
})

watch(
  () => props.images,
  () => {
    if (!count.value) {
      current.value = 0
      stopAutoplay()
      return
    }
    current.value = clampIndex(current.value)
    startAutoplay()
  },
  { deep: true },
)

onMounted(() => {
  startAutoplay()
})

onBeforeUnmount(() => {
  stopAutoplay()
})
</script>

<template>
  <section
    class="site-view-carousel"
    role="region"
    :aria-roledescription="'carousel'"
    :aria-label="ariaLabel"
    tabindex="0"
    @keydown="onKeydown"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
  >
    <div class="viewport">
      <div class="slides" @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd">
        <div
          v-for="(image, index) in images"
          :key="`slide-${index}`"
          class="slide"
          :class="{ active: index === current }"
          role="group"
          :aria-roledescription="'slide'"
          :aria-label="`${index + 1} de ${count}`"
        >
          <img
            v-if="image.object_name"
            :src="image.object_name"
            :alt="image.alt"
            class="main-image"
            draggable="false"
          />

          <div
            class="w-full flex justify-center bg-linear-to-t from-black/70 to-transparent absolute bottom-0 py-4"
          >
            <p v-if="image.description" class="text-white mt-2 px-4">"{{ image.description }}"</p>
          </div>
        </div>

        <div v-if="count === 0" class="slide placeholder active" aria-hidden="true">
          <div class="empty">Sin imagenes disponibles</div>
        </div>
      </div>

      <div v-if="showArrows && canNavigate" class="arrows">
        <button type="button" class="arrow prev" aria-label="Anterior" @click="prev">‹</button>
        <button type="button" class="arrow next" aria-label="Siguiente" @click="next">›</button>
      </div>
    </div>

    <div v-if="showThumbnails && count > 0" class="thumbnails" role="tablist">
      <button
        v-for="(image, index) in images"
        :key="`thumb-${index}`"
        class="thumb"
        :class="{ active: index === current }"
        type="button"
        role="tab"
        :aria-selected="index === current"
        :aria-label="`Mostrar imagen ${index + 1}`"
        @click="goTo(index)"
      >
        <img v-if="image.object_name" :src="image.object_name" :alt="image.alt" draggable="false" />
      </button>
    </div>
  </section>
</template>

<style scoped>
.site-view-carousel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  outline: none;
}

.viewport {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  background: #0f172a;
  min-height: 320px;
  max-height: 70vh;
}

.slides {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  max-height: 100%;
}

.slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 320ms ease;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  max-height: 100%;
  background: #0b1220;
}

.slide.active {
  opacity: 1;
  pointer-events: auto;
}

.main-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}

.placeholder .empty {
  color: #94a3b8;
  font-size: 0.95rem;
}

.arrows {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  pointer-events: none;
}

.arrow {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  border: none;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.55);
  color: #fff;
  font-size: 1.75rem;
  cursor: pointer;
  transition:
    background 200ms ease,
    transform 200ms ease;
  pointer-events: auto;
}

.arrow:hover {
  background: rgba(15, 23, 42, 0.8);
}

.arrow:active {
  transform: scale(0.95);
}

.thumbnails {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.thumb {
  position: relative;
  width: 96px;
  height: 72px;
  border: none;
  padding: 0;
  border-radius: 0.75rem;
  overflow: hidden;
  cursor: pointer;
  background: transparent;
  outline: none;
  transition: transform 200ms ease;
}

.thumb::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.4);
  opacity: 0;
  transition: opacity 200ms ease;
}

.thumb:hover {
  transform: translateY(-2px);
}

.thumb.active::after {
  opacity: 1;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 768px) {
  .site-view-carousel {
    gap: 1rem;
  }

  .viewport {
    min-height: 240px;
    max-height: 60vh;
  }

  .slides {
    aspect-ratio: 4 / 3;
  }

  .thumb {
    width: 80px;
    height: 60px;
  }
}

@media (max-width: 480px) {
  .viewport {
    min-height: 200px;
    max-height: 55vh;
  }

  .slides {
    aspect-ratio: 3 / 4;
  }

  .thumb {
    width: 64px;
    height: 48px;
  }
}
</style>
