<script setup>
import { ref, onMounted } from 'vue'
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
}

const goToDetail = (id) => {
  router.push(`/movie/${id}`)
}

onMounted(() => {
  fetchMovies()
  fetchGenres()
})
</script>

<template>
  <div class="home">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索电影名称、导演、演员..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @clear="handleSearch"
        style="width: 400px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" size="large" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">类型：</span>
        <el-radio-group v-model="selectedGenre" @change="handleSearch">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button v-for="g in genres" :key="g" :value="g">{{ g }}</el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-group">
        <span class="filter-label">排序：</span>
        <el-radio-group v-model="sortBy" @change="handleSearch">
          <el-radio-button value="rating">评分最高</el-radio-button>
          <el-radio-button value="year">最新上映</el-radio-button>
          <el-radio-button value="title">名称排序</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 电影列表 -->
    <div v-loading="loading" class="movie-grid">
      <el-card
        v-for="movie in movies"
        :key="movie.id"
        class="movie-card"
        @click="goToDetail(movie.id)"
        shadow="hover"
      >
        <div class="movie-poster">
          <img
            v-if="movie.poster_url"
            :src="movie.poster_url"
            :alt="movie.title"
          />
          <div v-else class="poster-placeholder">
            <el-icon :size="48"><Film /></el-icon>
          </div>
          <div class="movie-rating-badge">
            <el-icon><Star /></el-icon>
            {{ movie.avg_rating }}
          </div>
        </div>
        <div class="movie-info">
          <h3 class="movie-title">{{ movie.title }}</h3>
          <p class="movie-meta">{{ movie.year }} · {{ movie.genres.join(' / ') }}</p>
          <p class="movie-director">{{ movie.director }}</p>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && movies.length === 0" description="暂无电影数据" />

    <!-- 分页 -->
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.home {
  padding-bottom: 20px;
}

.search-bar {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.movie-card {
  cursor: pointer;
  transition: transform 0.2s;
  overflow: hidden;
}

.movie-card:hover {
  transform: translateY(-4px);
}

.movie-poster {
  position: relative;
  width: 100%;
  height: 280px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  color: #c0c4cc;
}

.movie-rating-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 193, 7, 0.9);
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.movie-info {
  padding: 12px 0 0;
}

.movie-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.movie-director {
  font-size: 12px;
  color: #909399;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
