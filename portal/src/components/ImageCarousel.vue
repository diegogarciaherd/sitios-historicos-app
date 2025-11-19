<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import SiteCard from './SiteCard.vue'
import { RouterLink } from 'vue-router'

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
const nextIndex = computed(() => clampIndex(current.value + 1))
const next2Index = computed(() => clampIndex(current.value + 2))

// Índices visibles para tarjetas de sitio: activa, siguiente y siguiente2 (si existen)
const visibleIndices = computed(() => {
  if (count.value <= 0) return []
  if (count.value === 1) return [current.value]
  if (count.value === 2) return [current.value, nextIndex.value]
  return [current.value, nextIndex.value, next2Index.value]
})

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

// Soporte para touchscreens
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
          <div v-if="img.caption" class="caption">
            <div class="flex flex-col gap-14">
              <div class="caption-inner">
                <h1 class="caption-title">{{ img.caption.title.toUpperCase() }}</h1>
                <p class="caption-subtitle">{{ img.caption.subtitle }}</p>
              </div>
              <div>
                <RouterLink class="px-12 py-4 text-white bg-sky-950 rounded-lg" to="/"
                  >Explorar →</RouterLink
                >
              </div>
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

    <div v-if="visibleIndices.length" class="sitecards" aria-hidden="false">
      <div
        v-for="(idx, pos) in visibleIndices"
        :key="idx"
        class="card"
        :class="{ main: pos === 0, next: pos === 1, next2: pos === 2 }"
      >
        <SiteCard :site="images[idx]?.sitio" @click="goTo(idx)" />
      </div>
    </div>

    <div v-if="showArrows && canNavigate" class="nav-under">
      <button class="nav prev text-2xl" type="button" aria-label="Anterior" @click="prev">‹</button>
      <button class="nav next text-2xl" type="button" aria-label="Siguiente" @click="next">
        ›
      </button>
    </div>

    <div
      v-if="showIndicators && canNavigate"
      class="indicators"
      role="tablist"
      aria-orientation="vertical"
    >
      <template v-for="(img, i) in images" :key="`ind-${i}`">
        <div class="dot-wrap">
          <button
            class="dot"
            :class="{ active: i === current }"
            role="tab"
            :aria-selected="i === current"
            :aria-label="`Ir a la diapositiva ${i + 1}`"
            @click="goTo(i)"
          >
            <span v-if="i === current">{{ i + 1 }}</span>
          </button>
        </div>
        <div v-if="i < count - 1" class="connector" aria-hidden="true" />
      </template>
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
  overflow: hidden; /* oculta desborde horizontal de sitecards para evitar scrollbar */
}
.carousel:focus-visible {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.6);
}

.indicators {
  position: absolute;
  top: 10rem;
  bottom: 10rem;
  left: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 30; /* por encima de las slides/caption */
  width: 2.25rem; /* ancho suficiente para el dot con número */
}
.dot-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}
.connector {
  width: 2px;
  background: rgba(255, 255, 255, 0.45);
  flex: 1 1 auto;
  margin: 0.35rem 0;
  align-self: center;
}

.dot {
  width: 1rem;
  height: 1rem;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.18);
  cursor: pointer;
  padding: 0;
  display: grid;
  place-items: center;
  color: transparent;
  font-weight: 700;
  font-size: 0.8rem;
  line-height: 1;
  transition: transform 250ms ease;
}
.dot.active {
  transform: scale(2);
  color: #fff;
  transition: transform 250ms ease;
}

.slide {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  user-select: none;
  opacity: 0;
  transition: opacity 450ms ease-out;
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
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  padding-left: 15%;
  padding-right: 8%;
  pointer-events: none; /* evita tapar flechas/indicadores */
}
.caption-inner {
  color: #fff;
  max-width: min(48ch, 50%);
}
.caption-title {
  font-size: clamp(2rem, 6vw, 5rem);
  line-height: 1.05;
  margin: 0 0 0.5rem;
}
.caption-subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  opacity: 0.9;
}

/* Arrows */
.nav {
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
  z-index: 30;
}
.nav:hover {
  background: rgba(17, 24, 39, 0.75);
}
.nav:active {
  transform: scale(0.96);
}

/* (El bloque antiguo de indicadores se eliminó para evitar conflictos) */

/* Placeholder */
.placeholder .empty {
  color: #94a3b8;
  font-size: 0.9rem;
}

/* SiteCards overlay */
.sitecards {
  position: absolute;
  top: 50%;
  left: 70%;
  transform: translateY(-50%);
  z-index: 25; /* debajo de flechas/indicadores, encima de imagen */
  pointer-events: auto; /* permitir interacción con cards */
}
.card {
  position: absolute;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  transition:
    transform 350ms ease,
    opacity 350ms ease,
    filter 350ms ease;
  will-change: transform, opacity, filter;
  overflow: hidden;
}
.card.main {
  transform: translateY(-50%) translateX(0) scale(1);
  opacity: 1;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
  z-index: 3;
}
.card.next {
  transform: translateY(-50%) translateX(380px) scale(0.9);
  opacity: 0.95;
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.2));
  z-index: 2;
}
.card.next2 {
  transform: translateY(-50%) translateX(760px) scale(0.82);
  opacity: 0.8;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.18));
  z-index: 1;
}

/* Smaller screens adjust aspect ratio */
@media (max-width: 1024px) {
  .card {
    right: -100px;
  }
  .card.next {
    transform: translateY(-50%) translateX(280px) scale(0.88);
  }
  .card.next2 {
    transform: translateY(-50%) translateX(520px) scale(0.8);
  }
}

@media (max-width: 768px) {
  .card.next {
    transform: translateY(-50%) translateX(200px) scale(0.86);
  }
  .card.next2 {
    transform: translateY(-50%) translateX(360px) scale(0.78);
  }
}

@media (max-width: 640px) {
  .carousel {
    aspect-ratio: 4/3;
  }
}

/* Contenedor de flechas bajo las SiteCards */
.nav-under {
  position: absolute;
  top: 75%;
  left: 55%;
  transform: translate(-50%, 220%); /* más abajo de las cards */
  display: flex;
  gap: 0.5rem;
  z-index: 30;
}
</style>
