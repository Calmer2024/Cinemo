<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { moviesAPI, ratingsAPI, recommendationsAPI } from '../api'

const route = useRoute()
const router = useRouter()
const movieId = ref(route.params.id)

const movie = ref(null)
const ratings = ref([])
const similarMovies = ref([])
const loading = ref(true)

const isLoggedIn = !!localStorage.getItem('token')
const myScore = ref(0)
const myReview = ref('')
const submitting = ref(false)

const ratingsPage = ref(1)
const ratingsTotal = ref(0)
const brokenPosters = ref(new Set())

const posterKey = (item, scope = 'poster') => `${scope}:${item?.id ?? item?.poster_url}`

const hasPoster = (item, scope = 'poster') => {
  return !!item?.poster_url && !brokenPosters.value.has(posterKey(item, scope))
}

const markPosterBroken = (item, scope = 'poster') => {
  brokenPosters.value = new Set(brokenPosters.value).add(posterKey(item, scope))
}

const fetchMovie = async () => {
  loading.value = true
  try {
    const res = await moviesAPI.get(movieId.value)
    movie.value = res.movie
  } finally {
    loading.value = false
  }
}

const fetchRatings = async () => {
  const res = await ratingsAPI.getByMovie(movieId.value, { page: ratingsPage.value, per_page: 10 })
  ratings.value = res.ratings
  ratingsTotal.value = res.total
}

const fetchSimilar = async () => {
  const res = await recommendationsAPI.similar(movieId.value)
  similarMovies.value = res.similar
}

const submitRating = async () => {
  if (myScore.value === 0) {
    ElMessage.warning('请选择评分')
    return
  }
  submitting.value = true
  try {
    await ratingsAPI.create({
      movie_id: parseInt(movieId.value),
      score: myScore.value,
      review: myReview.value
    })
    ElMessage.success('评分成功')
    myReview.value = ''
    fetchMovie()
    fetchRatings()
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    submitting.value = false
  }
}

const scoreLabels = ['很差', '较差', '一般', '推荐', '力荐']

const loadAll = () => {
  window.scrollTo({ top: 0, behavior: 'instant' })
  movie.value = null
  ratings.value = []
  similarMovies.value = []
  myScore.value = 0
  myReview.value = ''
  ratingsPage.value = 1
  fetchMovie()
  fetchRatings()
  fetchSimilar()
}

// 监听路由参数变化，同一组件复用时重新加载
watch(() => route.params.id, (newId) => {
  if (newId) {
    movieId.value = newId
    loadAll()
  }
})

onMounted(loadAll)
</script>

<template>
  <div class="detail-page" v-loading="loading">
    <template v-if="movie">
      <!-- Backdrop -->
      <div class="detail-backdrop">
        <img
          v-if="hasPoster(movie, 'backdrop')"
          :src="movie.poster_url"
          :alt="movie.title"
          @error.stop="markPosterBroken(movie, 'backdrop')"
        />
        <div class="detail-backdrop__overlay"></div>
      </div>

      <!-- Main Content -->
      <div class="detail-content">
        <!-- Hero Section -->
        <div class="detail-top-row">
          <div></div>
          <button class="back-btn animate-fade-in" @click="$router.back()">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M11 4L6 9l5 5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            返回
          </button>
        </div>
        <section class="detail-hero animate-fade-in-up">
          <div class="detail-hero__poster">
            <img
              v-if="hasPoster(movie)"
              :src="movie.poster_url"
              :alt="movie.title"
              @error.stop="markPosterBroken(movie)"
            />
            <div v-else class="poster-fallback">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/>
                <circle cx="18" cy="24" r="4" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="30" cy="24" r="4" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
          </div>

          <div class="detail-hero__info">
            <h1 class="detail-hero__title">{{ movie.title }}</h1>

            <div class="detail-hero__rating">
              <div class="rating-big">
                <span class="rating-big__number">{{ movie.avg_rating }}</span>
                <span class="rating-big__label">/ 5</span>
              </div>
              <span class="rating-count">{{ movie.rating_count }} 人评分</span>
            </div>

            <div class="detail-hero__tags">
              <span v-for="g in movie.genres" :key="g" class="tag">{{ g }}</span>
            </div>

            <div class="detail-meta">
              <div class="detail-meta__item">
                <span class="detail-meta__label">年份</span>
                <span class="detail-meta__value">{{ movie.year }}</span>
              </div>
              <div class="detail-meta__item">
                <span class="detail-meta__label">导演</span>
                <span class="detail-meta__value">{{ movie.director }}</span>
              </div>
              <div class="detail-meta__item">
                <span class="detail-meta__label">演员</span>
                <span class="detail-meta__value">{{ movie.actors }}</span>
              </div>
            </div>

            <p class="detail-hero__desc">{{ movie.description }}</p>
          </div>
        </section>

        <!-- Rating Section -->
        <section v-if="isLoggedIn" class="rate-section animate-fade-in-up delay-2">
          <h2 class="section-title">为这部电影评分</h2>
          <div class="rate-form">
            <div class="rate-stars">
              <button
                v-for="i in 5"
                :key="i"
                class="rate-star"
                :class="{ 'rate-star--active': i <= myScore, 'rate-star--hover': i <= myScore }"
                @click="myScore = i"
              >
                <svg width="28" height="28" viewBox="0 0 14 14" fill="currentColor">
                  <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
                </svg>
              </button>
              <span class="rate-stars__label" v-if="myScore > 0">{{ scoreLabels[myScore - 1] }}</span>
            </div>
            <textarea
              v-model="myReview"
              class="rate-textarea"
              placeholder="写下你的评价（可选）"
              rows="3"
              maxlength="500"
            ></textarea>
            <button
              class="btn btn--accent"
              :class="{ 'btn--loading': submitting }"
              :disabled="submitting"
              @click="submitRating"
            >
              {{ submitting ? '提交中...' : '提交评分' }}
            </button>
          </div>
        </section>

        <!-- Reviews Section -->
        <section class="reviews-section animate-fade-in-up delay-3">
          <h2 class="section-title">用户评价 <span class="section-title__count">{{ ratingsTotal }}</span></h2>

          <div v-if="ratings.length === 0" class="empty-reviews">
            <p>暂无评价，来写第一条吧</p>
          </div>

          <div v-else class="reviews-list">
            <article v-for="r in ratings" :key="r.id" class="review-item">
              <div class="review-item__header">
                <div class="review-item__avatar">
                  {{ (r.username || '匿').charAt(0).toUpperCase() }}
                </div>
                <div class="review-item__meta">
                  <span class="review-item__name">{{ r.username || '匿名用户' }}</span>
                  <div class="review-item__stars">
                    <svg v-for="i in 5" :key="i" width="14" height="14" viewBox="0 0 14 14" :fill="i <= r.score ? 'var(--accent)' : 'var(--text-tertiary)'">
                      <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
                    </svg>
                  </div>
                  <span class="review-item__date">{{ new Date(r.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
              <p v-if="r.review" class="review-item__text">{{ r.review }}</p>
            </article>
          </div>

          <div v-if="ratingsTotal > 10" class="pagination-wrap">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="ratingsTotal"
              :page-size="10"
              @current-change="(p) => { ratingsPage = p; fetchRatings() }"
            />
          </div>
        </section>

        <!-- Similar Movies -->
        <section v-if="similarMovies.length > 0" class="similar-section animate-fade-in-up delay-4">
          <h2 class="section-title">相似推荐</h2>
          <div class="similar-scroll">
            <article
              v-for="m in similarMovies"
              :key="m.id"
              class="similar-card"
              @click="router.push(`/movie/${m.id}`)"
            >
              <div class="similar-card__poster">
                <img
                  v-if="hasPoster(m, 'similar')"
                  :src="m.poster_url"
                  :alt="m.title"
                  loading="lazy"
                  @error.stop="markPosterBroken(m, 'similar')"
                />
                <div v-else class="poster-fallback-sm">
                  <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
                    <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
              </div>
              <div class="similar-card__body">
                <p class="similar-card__title">{{ m.title }}</p>
                <p class="similar-card__rating">{{ m.avg_rating }}</p>
              </div>
            </article>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-page {
  position: relative;
}

/* Backdrop */
.detail-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 500px;
  overflow: hidden;
  z-index: 0;
}

.detail-backdrop img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(40px) brightness(0.3);
  transform: scale(1.2);
}

.detail-backdrop__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, var(--bg-primary) 100%);
}

/* Content */
.detail-content {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px 60px;
  display: flex;
  flex-direction: column;
  gap: 48px;
}

/* Top Row with Back Button */
.detail-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Back Button */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-medium);
  background: var(--bg-card);
}

/* Hero */
.detail-hero {
  display: flex;
  gap: 36px;
}

.detail-hero__poster {
  flex-shrink: 0;
  width: 260px;
  height: 380px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  background: var(--bg-elevated);
}

.detail-hero__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.detail-hero__info {
  flex: 1;
  min-width: 0;
}

.detail-hero__title {
  font-size: clamp(1.8rem, 3vw, 2.5rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.detail-hero__rating {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
}

.rating-big__number {
  font-size: 36px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}

.rating-big__label {
  font-size: 16px;
  color: var(--text-tertiary);
}

.rating-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tag {
  padding: 4px 14px;
  background: var(--accent-dim);
  border: 1px solid rgba(232, 168, 56, 0.2);
  color: var(--accent);
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 500;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.detail-meta__item {
  display: flex;
  gap: 12px;
}

.detail-meta__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  min-width: 40px;
}

.detail-meta__value {
  font-size: 14px;
  color: var(--text-primary);
}

.detail-hero__desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

/* Section Title */
.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
  letter-spacing: -0.01em;
}

.section-title__count {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-tertiary);
  margin-left: 8px;
}

/* Rate Section */
.rate-section {
  padding: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
}

.rate-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rate-stars {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rate-star {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 4px;
  transition: all 0.15s ease;
  display: flex;
}

.rate-star:hover,
.rate-star--active {
  color: var(--accent);
  transform: scale(1.15);
}

.rate-stars__label {
  margin-left: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--accent);
}

.rate-textarea {
  width: 100%;
  padding: 14px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s ease;
}

.rate-textarea:focus {
  border-color: var(--accent);
}

.rate-textarea::placeholder {
  color: var(--text-tertiary);
}

/* Reviews */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.review-item {
  padding: 20px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.review-item:last-child {
  border-bottom: none;
}

.review-item__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.review-item__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.review-item__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.review-item__name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.review-item__stars {
  display: flex;
  gap: 2px;
}

.review-item__date {
  font-size: 12px;
  color: var(--text-tertiary);
}

.review-item__text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  padding-left: 48px;
}

.empty-reviews {
  text-align: center;
  padding: 40px;
  color: var(--text-tertiary);
}

.empty-reviews p {
  margin: 0;
}

/* Similar Movies */
.similar-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  -webkit-overflow-scrolling: touch;
}

.similar-scroll::-webkit-scrollbar {
  height: 4px;
}

.similar-card {
  flex-shrink: 0;
  width: 140px;
  cursor: pointer;
  transition: transform 0.3s var(--ease-out-expo);
}

.similar-card:hover {
  transform: translateY(-4px);
}

.similar-card__poster {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-elevated);
  margin-bottom: 10px;
}

.similar-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-fallback-sm {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.similar-card__body {
  padding: 0 4px;
}

.similar-card__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.similar-card__rating {
  font-size: 13px;
  color: var(--accent);
  font-weight: 600;
  margin: 0;
}

/* Pagination */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* Responsive */
@media (max-width: 768px) {
  .detail-hero {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .detail-hero__poster {
    width: 200px;
    height: 290px;
  }

  .detail-hero__tags {
    justify-content: center;
  }

  .detail-hero__rating {
    justify-content: center;
  }

  .detail-content {
    padding: 24px 16px 40px;
    gap: 32px;
  }

  .rate-section {
    padding: 24px 20px;
  }

  .review-item__text {
    padding-left: 0;
  }
}
</style>
