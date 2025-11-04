<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => [], // [{ src, alt?, caption?, href? }]
  },
  autoplay: { type: Boolean, default: true },
  interval: { type: Number, default: 4000 },
  loop: { type: Boolean, default: true },
  showIndicators: { type: Boolean, default: true },
  showArrows: { type: Boolean, default: true },
  pauseOnHover: { type: Boolean, default: true },
  ariaLabel: { type: String, default: 'Carrusel de imágenes' },
})

const emit = defineEmits(['change'])

const current = ref(0)
const hovering = ref(false)
let timerId = null

const count = computed(() => props.images?.length || 0)
const canNavigate = computed(() => count.value > 1)

function clampIndex(i) {
  if (count.value === 0) return 0
  if (props.loop) return (i + count.value) % count.value
  return Math.min(Math.max(i, 0), count.value - 1)
}

function goTo(i) {
  const next = clampIndex(i)
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

// Swipe support
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchActive = ref(false)

function onTouchStart(e) {
  if (!canNavigate.value) return
  const t = e.touches?.[0]
  if (!t) return
  touchActive.value = true
  touchStartX.value = t.clientX
  touchStartY.value = t.clientY
}

function onTouchEnd(e) {
  if (!touchActive.value) return
  touchActive.value = false
  const t = e.changedTouches?.[0]
  if (!t) return
  const dx = t.clientX - touchStartX.value
  const dy = t.clientY - touchStartY.value
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 40) {
    dx < 0 ? next() : prev()
  }
}

function onKeydown(e) {
  if (!canNavigate.value) return
  if (e.key === 'ArrowRight') {
    e.preventDefault()
    next()
  }
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    prev()
  }
}

watch(() => props.autoplay, startAutoplay)
watch(() => props.interval, startAutoplay)
watch(count, startAutoplay)

onMounted(() => {
  startAutoplay()
})

onBeforeUnmount(() => {
  stopAutoplay()
})
</script>

<template>
  <section
    class="carousel"
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
          v-for="(img, i) in images"
          :key="i"
          class="slide"
          :class="{ active: i === current }"
          role="group"
          :aria-roledescription="'slide'"
          :aria-label="`${i + 1} de ${count}`"
        >
          <a v-if="img.href" class="media" :href="img.href" draggable="false">
            <img :src="img.src" :alt="img.alt || ''" draggable="false" />
          </a>
          <div v-else class="media">
            <img :src="img.src" :alt="img.alt || ''" draggable="false" />
          </div>
          <div v-if="img.caption" class="caption absolute inset-0 flex items-center px-8">
            <div>
              <h1 class="text-[5rem]">{{ img.caption.title.toUpperCase() }}</h1>
              <p>{{ img.caption.subtitle }}</p>
            </div>
          </div>
        </div>

        <div v-if="count === 0" class="slide placeholder active" aria-hidden="true">
          <div class="media">
            <div class="empty">Sin imágenes</div>
          </div>
        </div>
      </div>
    </div>

    <button
      v-if="showArrows && canNavigate"
      class="nav prev"
      type="button"
      aria-label="Anterior"
      @click="prev"
    >
      ‹
    </button>
    <button
      v-if="showArrows && canNavigate"
      class="nav next"
      type="button"
      aria-label="Siguiente"
      @click="next"
    >
      ›
    </button>

    <div v-if="showIndicators && canNavigate" class="indicators" role="tablist">
      <button
        v-for="(img, i) in images"
        :key="`dot-${i}`"
        class="dot"
        :class="{ active: i === current }"
        role="tab"
        :aria-selected="i === current"
        :aria-label="`Ir a la diapositiva ${i + 1}`"
        @click="goTo(i)"
      />
    </div>
  </section>
</template>

<style scoped>
.carousel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: #0f172a08;
  outline: none;
}
.carousel:focus-visible {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.6);
}

.viewport {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.slides {
  position: relative;
  width: 100%;
  height: 100%;
}

.slide {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  user-select: none;
  opacity: 0;
  transition: opacity 450ms ease-in;
  pointer-events: none;
}
.slide.active {
  opacity: 1;
  z-index: 2;
  pointer-events: auto;
}

.media {
  width: 100%;
  height: 100%;
  background: #0b1220;
  display: grid;
  place-items: center;
}
.media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.caption {
  padding: 0.5rem 0.75rem;
  color: #fff;
  pointer-events: none; /* evita tapar flechas/indicadores */
}

/* Arrows */
.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  border: none;
  display: grid;
  place-items: center;
  background: rgba(17, 24, 39, 0.55);
  color: white;
  cursor: pointer;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
  z-index: 30; /* por encima de las slides/caption */
}
.nav:hover {
  background: rgba(17, 24, 39, 0.75);
}
.nav:active {
  transform: translateY(-50%) scale(0.96);
}
.nav.prev {
  left: 0.5rem;
}
.nav.next {
  right: 0.5rem;
}

/* Indicators */
.indicators {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0.5rem;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  z-index: 30; /* por encima de las slides/caption */
}
.dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  border: none;
  background: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  padding: 0;
}
.dot.active {
  background: #6366f1;
}

/* Placeholder */
.placeholder .empty {
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Smaller screens adjust aspect ratio */
@media (max-width: 640px) {
  .carousel {
    aspect-ratio: 4/3;
  }
}
</style>
