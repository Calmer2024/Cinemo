<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { moviesAPI } from '../api'

const router = useRouter()

const movies = ref([])
const genres = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const searchQuery = ref('')
const selectedGenre = ref('')
const sortBy = ref('rating')

const fetchMovies = async () => {
  loading.value = true
  try {
    const res = await moviesAPI.list({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchQuery.value,
      genre: selectedGenre.value,
      sort_by: sortBy.value
    })
    movies.value = res.movies
    total.value = res.total
    await nextTick()
    observeCards()
  } finally {
    loading.value = false
  }
}

const fetchGenres = async () => {
  const res = await moviesAPI.genres()
  genres.value = res.genres
}

const handleSearch = () => {
  currentPage.value = 1
  fetchMovies()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchMovies()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goToDetail = (id) => {
  router.push(`/movie/${id}`)
}

// Intersection Observer for scroll animations
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
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' })

  document.querySelectorAll('.movie-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.06}s`
    observer.observe(el)
  })
}

onMounted(() => {
  fetchMovies()
  fetchGenres()
})
</script>

<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero__bg">
        <div class="hero__gradient"></div>
        <div class="hero__noise"></div>
      </div>
      <div class="hero__content">
        <h1 class="hero__title">
          发现你的下一部<span class="hero__accent">挚爱</span>电影
        </h1>
        <p class="hero__sub">
          基于协同过滤算法，为你智能推荐可能喜欢的电影
        </p>
        <div class="hero__search">
          <div class="search-input">
            <svg class="search-input__icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="9" cy="9" r="6" stroke="currentColor" stroke-width="1.5"/>
              <path d="M13.5 13.5L17 17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索电影名称、导演、演员..."
              @keyup.enter="handleSearch"
            />
            <button v-if="searchQuery" class="search-input__clear" @click="searchQuery = ''; handleSearch()">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <button class="btn btn--accent btn--lg" @click="handleSearch">搜索</button>
        </div>
      </div>
    </section>

    <!-- Filters -->
    <section class="filters">
      <div class="filters__inner">
        <div class="filters__row">
          <span class="filters__label">类型</span>
          <div class="filters__pills">
            <button
              class="pill"
              :class="{ 'pill--active': selectedGenre === '' }"
              @click="selectedGenre = ''; handleSearch()"
            >全部</button>
            <button
              v-for="g in genres"
              :key="g"
              class="pill"
              :class="{ 'pill--active': selectedGenre === g }"
              @click="selectedGenre = g; handleSearch()"
            >{{ g }}</button>
          </div>
        </div>
        <div class="filters__row">
          <span class="filters__label">排序</span>
          <div class="filters__pills">
            <button class="pill" :class="{ 'pill--active': sortBy === 'rating' }" @click="sortBy = 'rating'; handleSearch()">评分最高</button>
            <button class="pill" :class="{ 'pill--active': sortBy === 'year' }" @click="sortBy = 'year'; handleSearch()">最新上映</button>
            <button class="pill" :class="{ 'pill--active': sortBy === 'title' }" @click="sortBy = 'title'; handleSearch()">名称排序</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Movie Grid -->
    <section class="movies-section">
      <div v-if="loading" class="loading-grid">
        <div v-for="i in 12" :key="i" class="skeleton-card">
          <div class="skeleton-poster"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-text skeleton-text--short"></div>
        </div>
      </div>

      <div v-else class="movie-grid">
        <article
          v-for="movie in movies"
          :key="movie.id"
          class="movie-card"
          @click="goToDetail(movie.id)"
        >
          <div class="movie-card__poster">
            <img
              v-if="movie.poster_url"
              :src="movie.poster_url"
              :alt="movie.title"
              loading="lazy"
            />
            <div v-else class="movie-card__placeholder">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" stroke-width="2"/>
                <circle cx="18" cy="24" r="4" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="30" cy="24" r="4" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
            <div class="movie-card__overlay">
              <div class="movie-card__rating">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
                  <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
                </svg>
                {{ movie.avg_rating }}
              </div>
            </div>
          </div>
          <div class="movie-card__body">
            <h3 class="movie-card__title">{{ movie.title }}</h3>
            <p class="movie-card__meta">{{ movie.year }} - {{ movie.director }}</p>
          </div>
        </article>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && movies.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <rect x="8" y="14" width="48" height="36" rx="6" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <circle cx="24" cy="32" r="6" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <circle cx="40" cy="32" r="6" stroke="currentColor" stroke-width="2" opacity="0.3"/>
        </svg>
        <p>暂无匹配的电影</p>
        <button class="btn btn--ghost" @click="searchQuery = ''; selectedGenre = ''; handleSearch()">清除筛选</button>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="pagination-wrap">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
/* --- Hero --- */
.hero {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 24px 60px;
  overflow: hidden;
}

.hero__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero__gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 50% 20%, rgba(232, 168, 56, 0.08), transparent),
    radial-gradient(ellipse 60% 50% at 20% 80%, rgba(232, 168, 56, 0.04), transparent),
    linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.hero__noise {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  pointer-events: none;
}

.hero__content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 680px;
  animation: fadeInUp 0.8s var(--ease-out-expo) both;
}

.hero__title {
  font-size: clamp(2.2rem, 5vw, 3.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.hero__accent {
  color: var(--accent);
}

.hero__sub {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 36px;
  line-height: 1.6;
}

.hero__search {
  display: flex;
  gap: 12px;
  max-width: 520px;
  margin: 0 auto;
}

.search-input {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-input__icon {
  position: absolute;
  left: 16px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-input input {
  width: 100%;
  padding: 14px 44px 14px 48px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s ease;
}

.search-input input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.search-input input::placeholder {
  color: var(--text-tertiary);
}

.search-input__clear {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 4px;
  display: flex;
  transition: color 0.2s ease;
}

.search-input__clear:hover {
  color: var(--text-primary);
}

.btn--lg {
  padding: 14px 28px;
  font-size: 15px;
}

/* --- Filters --- */
.filters {
  padding: 0 24px;
  margin-bottom: 40px;
}

.filters__inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.filters__row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filters__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  min-width: 40px;
}

.filters__pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill {
  padding: 6px 16px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.pill:hover {
  border-color: var(--border-medium);
  color: var(--text-primary);
}

.pill--active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-on-accent);
}

/* --- Movie Grid --- */
.movies-section {
  padding: 0 24px 60px;
  max-width: 1328px;
  margin: 0 auto;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.movie-card {
  cursor: pointer;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  transition: all 0.35s var(--ease-out-expo);
  opacity: 0;
  transform: translateY(20px);
}

.movie-card.is-visible {
  animation: fadeInUp 0.5s var(--ease-out-expo) both;
}

.movie-card:hover {
  transform: translateY(-6px);
  border-color: var(--accent);
  box-shadow: var(--shadow-card-hover), 0 0 30px rgba(232, 168, 56, 0.08);
}

.movie-card__poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: var(--bg-elevated);
}

.movie-card__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-out-expo);
}

.movie-card:hover .movie-card__poster img {
  transform: scale(1.05);
}

.movie-card__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.movie-card__overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 40px 12px 12px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.movie-card:hover .movie-card__overlay {
  opacity: 1;
}

.movie-card__rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent);
  color: var(--text-on-accent);
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 700;
}

.movie-card__body {
  padding: 14px 16px 16px;
}

.movie-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-card__meta {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* --- Skeleton Loading --- */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

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

/* --- Empty State --- */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
}

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 15px;
}

/* --- Pagination --- */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* --- Responsive --- */
@media (max-width: 768px) {
  .hero {
    min-height: 320px;
    padding: 60px 20px 40px;
  }

  .hero__search {
    flex-direction: column;
  }

  .filters__row {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters__pills {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
  }

  .movie-grid,
  .loading-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }
}
</style>
