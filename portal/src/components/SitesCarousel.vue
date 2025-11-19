<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DetailedSiteCard from './DetailedSiteCard.vue'

const props = defineProps({
  sites: {
    type: Array,
    default: () => [],
  },
  autoplay: { type: Boolean, default: true },
  interval: { type: Number, default: 4500 },
  loop: { type: Boolean, default: true },
  showIndicators: { type: Boolean, default: true },
  showArrows: { type: Boolean, default: true },
  pauseOnHover: { type: Boolean, default: true },
  ariaLabel: { type: String, default: 'Carrusel de sitios' },
})

const emit = defineEmits(['change'])

const current = ref(0)
const hovering = ref(false)
let timerId = null

const count = computed(() => props.sites?.length || 0)
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

const visibleCards = computed(() => {
  if (count.value === 0) return []
  const slots = []
  const used = new Set()

  function add(offset) {
    if (slots.length >= count.value) return
    const raw = current.value + offset
    let idx
    if (props.loop) {
      idx = clampIndex(raw)
    } else {
      if (raw < 0 || raw >= count.value) return
      idx = raw
    }
    if (used.has(idx)) return
    used.add(idx)
    slots.push({ index: idx, offset })
  }

  add(0)
  for (let step = 1; step <= 2; step++) {
    add(-step)
    add(step)
  }

  return slots.sort((a, b) => a.offset - b.offset)
})

function positionClass(offset) {
  if (offset <= -2) return 'pos--2'
  if (offset === -1) return 'pos--1'
  if (offset === 0) return 'pos-0'
  if (offset === 1) return 'pos-1'
  return 'pos-2'
}

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
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 36) {
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
watch(count, (newCount, oldCount) => {
  if (newCount === 0) {
    stopAutoplay()
    current.value = 0
    return
  }
  if (current.value >= newCount) {
    current.value = props.loop ? clampIndex(current.value) : newCount - 1
  }
  if (newCount !== oldCount) startAutoplay()
})

onMounted(() => {
  startAutoplay()
})

onBeforeUnmount(() => {
  stopAutoplay()
})
</script>

<template>
  <section
    v-if="sites.length"
    class="sites-carousel"
    role="region"
    :aria-roledescription="'carousel'"
    :aria-label="ariaLabel"
    tabindex="0"
    @keydown="onKeydown"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
  >
    <div class="viewport">
      <div class="track" @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd">
        <div
          v-for="card in visibleCards"
          :key="card.index"
          class="card"
          :class="positionClass(card.offset)"
          role="group"
          :aria-roledescription="'slide'"
          :aria-label="`${card.index + 1} de ${count}`"
        >
          <DetailedSiteCard
            v-if="sites[card.index]"
            :site="sites[card.index]"
            :classes="'w-35 h-50 md:w-60 md:h-80'"
            @click="
              card.index === current
                ? $router.push(`/sites/${sites[card.index]?.id || ''}`)
                : goTo(card.index)
            "
          />
        </div>

        <div v-if="count === 0" class="card empty" role="presentation">
          <div class="empty-state">Sin sitios disponibles</div>
        </div>
      </div>
    </div>

    <div v-if="showIndicators && canNavigate" class="indicators" role="tablist">
      <button
        v-for="(site, i) in sites"
        :key="`dot-${i}`"
        class="dot"
        role="tab"
        :class="{ active: i === current }"
        :aria-selected="i === current"
        :aria-label="`Ir al sitio ${i + 1}`"
        @click="goTo(i)"
      >
        <span v-if="i === current">{{ i + 1 }}</span>
      </button>
    </div>

    <RouterLink class="px-12 py-4 text-white bg-sky-950 rounded-lg">Ver todos</RouterLink>

    <div v-if="showArrows && canNavigate" class="nav">
      <button type="button" class="arrow prev" aria-label="Anterior" @click="prev">‹</button>
      <button type="button" class="arrow next" aria-label="Siguiente" @click="next">›</button>
    </div>
  </section>
  <div v-else class="text-center text-gray-500 py-16">No hay sitios para mostrar.</div>
</template>

<style scoped>
.sites-carousel {
  position: relative;
  width: 100%;
  padding: 5rem 3rem;
  color: white;
  overflow: hidden;
  outline: none;
}

.viewport {
  width: 100%;
  display: flex;
  justify-content: center;
}

.track {
  position: relative;
  width: min(1200px, 90vw);
  height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1500px;
}

.card {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translateY(-50%);
  transition:
    transform 320ms ease,
    opacity 320ms ease,
    filter 320ms ease;
  cursor: pointer;
  will-change: transform, opacity, filter;
  overflow: hidden;
}

.card.empty {
  position: static;
  transform: none;
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #cbd5f5;
  font-size: 1rem;
  opacity: 0.75;
}

.empty-state {
  padding: 1rem 2rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
}

.pos-0 {
  transform: translate(-50%, -50%) translateZ(0) scale(1);
  opacity: 1;
  filter: drop-shadow(0 15px 35px rgba(0, 0, 0, 0.35));
  z-index: 5;
}

.pos-1 {
  transform: translate(-50%, -50%) translateX(260px) translateY(-20px) rotateY(-28deg)
    translateZ(-160px) scale(0.9);
  opacity: 0.88;
  filter: drop-shadow(0 12px 28px rgba(0, 0, 0, 0.28));
  z-index: 4;
}

.pos--1 {
  transform: translate(-50%, -50%) translateX(-260px) translateY(-20px) rotateY(28deg)
    translateZ(-160px) scale(0.9);
  opacity: 0.88;
  filter: drop-shadow(0 12px 28px rgba(0, 0, 0, 0.28));
  z-index: 4;
}

.pos-2 {
  transform: translate(-50%, -50%) translateX(460px) translateY(-40px) rotateY(-43deg)
    translateZ(-320px) scale(0.78);
  opacity: 0.68;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.22));
  z-index: 3;
}

.pos--2 {
  transform: translate(-50%, -50%) translateX(-460px) translateY(-40px) rotateY(43deg)
    translateZ(-320px) scale(0.78);
  opacity: 0.68;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.22));
  z-index: 3;
}

.nav {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 1rem;
  z-index: 10;
}

.arrow {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 1.75rem;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition:
    background 200ms ease,
    transform 200ms ease;
}

.arrow:hover {
  background: rgba(15, 23, 42, 0.85);
}

.arrow:active {
  transform: scale(0.95);
}

.indicators {
  position: absolute;
  top: 0.4rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  z-index: 12;
}

.dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 999px;
  border: 2px solid rgba(0, 0, 0, 0.65);
  background: transparent;
  display: grid;
  place-items: center;
  color: transparent;
  font-size: 0.7rem;
  cursor: pointer;
  transition:
    transform 200ms ease,
    background 200ms ease,
    color 200ms ease;
}

.dot.active {
  transform: scale(2);
  font-size: 0.45rem;
  background: rgba(0, 0, 0, 0.65);
  color: white;
}

@media (max-width: 1024px) {
  .track {
    height: 360px;
  }

  .nav {
    display: none;
  }

  .pos-1 {
    transform: translate(-50%, -50%) translateX(200px) translateY(-18px) rotateY(-16deg)
      translateZ(-150px) scale(0.88);
  }

  .pos--1 {
    transform: translate(-50%, -50%) translateX(-200px) translateY(-18px) rotateY(16deg)
      translateZ(-150px) scale(0.88);
  }

  .pos-2 {
    transform: translate(-50%, -50%) translateX(360px) translateY(-34px) rotateY(-24deg)
      translateZ(-280px) scale(0.74);
  }

  .pos--2 {
    transform: translate(-50%, -50%) translateX(-360px) translateY(-34px) rotateY(24deg)
      translateZ(-280px) scale(0.74);
  }
}

@media (max-width: 768px) {
  .track {
    height: 320px;
  }

  .pos-1 {
    transform: translate(-50%, -50%) translateX(160px) translateY(-16px) rotateY(-14deg)
      translateZ(-130px) scale(0.86);
  }

  .pos--1 {
    transform: translate(-50%, -50%) translateX(-160px) translateY(-16px) rotateY(14deg)
      translateZ(-130px) scale(0.86);
  }

  .pos-2 {
    transform: translate(-50%, -50%) translateX(280px) translateY(-28px) rotateY(-22deg)
      translateZ(-250px) scale(0.7);
    opacity: 0.58;
  }

  .pos--2 {
    transform: translate(-50%, -50%) translateX(-280px) translateY(-28px) rotateY(22deg)
      translateZ(-250px) scale(0.7);
    opacity: 0.58;
  }

  .nav {
    bottom: 1.5rem;
  }
}

@media (max-width: 640px) {
  .sites-carousel {
    padding: 2rem 0 3rem;
  }

  .track {
    height: 280px;
  }

  .pos-1 {
    transform: translate(-50%, -50%) translateX(120px) translateY(-12px) rotateY(-12deg)
      translateZ(-110px) scale(0.84);
  }

  .pos--1 {
    transform: translate(-50%, -50%) translateX(-120px) translateY(-12px) rotateY(12deg)
      translateZ(-110px) scale(0.84);
  }

  .pos-2 {
    transform: translate(-50%, -50%) translateX(200px) translateY(-22px) rotateY(-20deg)
      translateZ(-220px) scale(0.66);
    opacity: 0.48;
  }

  .pos--2 {
    transform: translate(-50%, -50%) translateX(-200px) translateY(-22px) rotateY(20deg)
      translateZ(-220px) scale(0.66);
    opacity: 0.48;
  }
}
</style>
