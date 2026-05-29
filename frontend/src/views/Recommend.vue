<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { recommendationsAPI } from '../api'

const router = useRouter()
const recommendations = ref([])
const loading = ref(false)
const triggering = ref(false)

const fetchRecommendations = async () => {
  loading.value = true
  try {
    const res = await recommendationsAPI.list({ per_page: 20 })
    recommendations.value = res.recommendations
    await nextTick()
    observeCards()
  } finally {
    loading.value = false
  }
}

const triggerSpark = async () => {
  triggering.value = true
  try {
    await recommendationsAPI.trigger()
    ElMessage.success('推荐计算完成')
    fetchRecommendations()
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    triggering.value = false
  }
}

let observer = null
const observeCards = () => {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })
  document.querySelectorAll('.rec-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.06}s`
    observer.observe(el)
  })
}

onMounted(fetchRecommendations)
</script>

<template>
  <div class="recommend-page">
    <div class="recommend-header animate-fade-in-up">
      <div>
        <h1 class="recommend-header__title">个性化推荐</h1>
        <p class="recommend-header__sub">
          基于 Spark ALS 协同过滤算法，根据你的评分历史推荐可能喜欢的电影
        </p>
      </div>
      <button
        class="btn btn--accent"
        :class="{ 'btn--loading': triggering }"
        :disabled="triggering"
        @click="triggerSpark"
      >
        <svg v-if="!triggering" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M2 8a6 6 0 0111.3-2.8M14 2v4h-4M14 8a6 6 0 01-11.3 2.8M2 14v-4h4"/>
        </svg>
        <span v-if="triggering" class="btn__spinner"></span>
        {{ triggering ? '计算中...' : '重新计算推荐' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rec-grid">
      <div v-for="i in 8" :key="i" class="skeleton-card">
        <div class="skeleton-poster"></div>
        <div class="skeleton-text"></div>
        <div class="skeleton-text skeleton-text--short"></div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-else-if="recommendations.length > 0" class="rec-grid">
      <article
        v-for="rec in recommendations"
        :key="rec.id"
        class="rec-card"
        @click="router.push(`/movie/${rec.movie_id}`)"
      >
        <div class="rec-card__poster">
          <img v-if="rec.movie?.poster_url" :src="rec.movie.poster_url" :alt="rec.movie?.title" loading="lazy" />
          <div v-else class="rec-card__fallback">
            <svg width="40" height="40" viewBox="0 0 48 48" fill="none">
              <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="rec-card__score">
            <svg width="12" height="12" viewBox="0 0 14 14" fill="currentColor">
              <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
            </svg>
            预测 {{ rec.score.toFixed(1) }}
          </div>
        </div>
        <div class="rec-card__body">
          <h3 class="rec-card__title">{{ rec.movie?.title }}</h3>
          <p class="rec-card__meta">{{ rec.movie?.year }} - {{ rec.movie?.genres?.join(' / ') }}</p>
        </div>
      </article>
    </div>

    <!-- Empty -->
    <div v-else class="empty-state animate-fade-in">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="28" r="12" stroke="currentColor" stroke-width="2" opacity="0.3"/>
        <path d="M20 50c0-6.6 5.4-12 12-12s12 5.4 12 12" stroke="currentColor" stroke-width="2" opacity="0.3"/>
        <path d="M44 24l6-6M50 24l-6-6" stroke="currentColor" stroke-width="2" opacity="0.3" stroke-linecap="round"/>
      </svg>
      <p>暂无推荐，先对一些电影评分再来</p>
      <button class="btn btn--accent" @click="router.push('/')">去发现电影</button>
    </div>
  </div>
</template>

<style scoped>
.recommend-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

.recommend-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 36px;
  gap: 20px;
}

.recommend-header__title {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.recommend-header__sub {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
  max-width: 500px;
}

.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.rec-card {
  cursor: pointer;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  transition: all 0.35s var(--ease-out-expo);
  opacity: 0;
  transform: translateY(20px);
}

.rec-card.is-visible {
  animation: fadeInUp 0.5s var(--ease-out-expo) both;
}

.rec-card:hover {
  transform: translateY(-6px);
  border-color: var(--accent);
  box-shadow: var(--shadow-card-hover), 0 0 30px rgba(232, 168, 56, 0.08);
}

.rec-card__poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: var(--bg-elevated);
}

.rec-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-out-expo);
}

.rec-card:hover .rec-card__poster img {
  transform: scale(1.05);
}

.rec-card__fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.rec-card__score {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent);
  color: var(--text-on-accent);
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 700;
}

.rec-card__body {
  padding: 14px 16px 16px;
}

.rec-card__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rec-card__meta {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Skeleton */
.skeleton-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
}

.skeleton-poster {
  width: 100%;
  aspect-ratio: 2/3;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card-hover) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  height: 14px;
  margin: 14px 16px 0;
  border-radius: 4px;
  background: var(--bg-elevated);
}

.skeleton-text--short {
  width: 60%;
  margin-bottom: 16px;
}

/* Empty */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
}

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0 0 24px;
  font-size: 15px;
}

.btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn--loading {
  opacity: 0.8;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .recommend-header {
    flex-direction: column;
  }

  .rec-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 14px;
  }
}
</style>
