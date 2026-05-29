<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { moviesAPI, ratingsAPI, recommendationsAPI } from '../api'

const route = useRoute()
const movieId = route.params.id

const movie = ref(null)
const ratings = ref([])
const similarMovies = ref([])
const loading = ref(true)

// 评分表单
const isLoggedIn = !!localStorage.getItem('token')
const myScore = ref(0)
const myReview = ref('')
const submitting = ref(false)

// 分页
const ratingsPage = ref(1)
const ratingsTotal = ref(0)

const fetchMovie = async () => {
  loading.value = true
  try {
    const res = await moviesAPI.get(movieId)
    movie.value = res.movie
  } finally {
    loading.value = false
  }
}

const fetchRatings = async () => {
  const res = await ratingsAPI.getByMovie(movieId, {
    page: ratingsPage.value,
    per_page: 10
  })
  ratings.value = res.ratings
  ratingsTotal.value = res.total
}

const fetchSimilar = async () => {
  const res = await recommendationsAPI.similar(movieId)
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
      movie_id: parseInt(movieId),
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

onMounted(() => {
  fetchMovie()
  fetchRatings()
  fetchSimilar()
})
</script>

<template>
  <div class="movie-detail" v-loading="loading">
    <template v-if="movie">
      <!-- 电影信息 -->
      <el-card class="info-card">
        <div class="movie-header">
          <div class="poster">
            <img v-if="movie.poster_url" :src="movie.poster_url" :alt="movie.title" />
            <div v-else class="poster-placeholder">
              <el-icon :size="64"><Film /></el-icon>
            </div>
          </div>
          <div class="info">
            <h1>{{ movie.title }}</h1>
            <div class="rating-display">
              <el-rate
                :model-value="movie.avg_rating"
                disabled
                show-score
                text-color="#ff9900"
                score-template="{value} 分"
              />
              <span class="rating-count">({{ movie.rating_count }} 人评分)</span>
            </div>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="年份">{{ movie.year }}</el-descriptions-item>
              <el-descriptions-item label="导演">{{ movie.director }}</el-descriptions-item>
              <el-descriptions-item label="演员">{{ movie.actors }}</el-descriptions-item>
              <el-descriptions-item label="类型">
                <el-tag v-for="g in movie.genres" :key="g" style="margin-right: 6px">{{ g }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
            <p class="description">{{ movie.description }}</p>
          </div>
        </div>
      </el-card>

      <!-- 评分区域 -->
      <el-card class="rate-card" v-if="isLoggedIn">
        <template #header>
          <span>为这部电影评分</span>
        </template>
        <div class="rate-form">
          <el-rate v-model="myScore" show-text :texts="['很差', '较差', '一般', '推荐', '力荐']" />
          <el-input
            v-model="myReview"
            type="textarea"
            :rows="3"
            placeholder="写下你的评价（可选）"
            maxlength="500"
            show-word-limit
          />
          <el-button type="primary" :loading="submitting" @click="submitRating">
            提交评分
          </el-button>
        </div>
      </el-card>

      <!-- 评论列表 -->
      <el-card class="reviews-card">
        <template #header>
          <span>用户评价 ({{ ratingsTotal }})</span>
        </template>
        <div v-if="ratings.length === 0" class="no-reviews">暂无评价</div>
        <div v-for="r in ratings" :key="r.id" class="review-item">
          <div class="review-header">
            <span class="reviewer">{{ r.username || '匿名用户' }}</span>
            <el-rate :model-value="r.score" disabled size="small" />
            <span class="review-time">{{ new Date(r.created_at).toLocaleDateString() }}</span>
          </div>
          <p v-if="r.review" class="review-text">{{ r.review }}</p>
        </div>
        <el-pagination
          v-if="ratingsTotal > 10"
          layout="prev, pager, next"
          :total="ratingsTotal"
          :page-size="10"
          @current-change="(p) => { ratingsPage = p; fetchRatings() }"
        />
      </el-card>

      <!-- 相似推荐 -->
      <el-card class="similar-card" v-if="similarMovies.length > 0">
        <template #header>
          <span>相似电影推荐</span>
        </template>
        <div class="similar-grid">
          <div
            v-for="m in similarMovies"
            :key="m.id"
            class="similar-item"
            @click="$router.push(`/movie/${m.id}`)"
          >
            <div class="similar-poster">
              <img v-if="m.poster_url" :src="m.poster_url" :alt="m.title" />
              <div v-else class="poster-placeholder-sm"><el-icon><Film /></el-icon></div>
            </div>
            <p class="similar-title">{{ m.title }}</p>
            <p class="similar-rating">⭐ {{ m.avg_rating }}</p>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.movie-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.movie-header {
  display: flex;
  gap: 24px;
}

.poster {
  flex-shrink: 0;
  width: 240px;
  height: 340px;
  overflow: hidden;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  color: #c0c4cc;
}

.info {
  flex: 1;
}

.info h1 {
  margin-bottom: 12px;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.rating-count {
  color: #909399;
  font-size: 13px;
}

.description {
  margin-top: 16px;
  color: #606266;
  line-height: 1.6;
}

.rate-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-item {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.review-item:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.reviewer {
  font-weight: 500;
}

.review-time {
  color: #909399;
  font-size: 12px;
}

.review-text {
  color: #606266;
  margin: 0;
}

.no-reviews {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.similar-grid {
  display: flex;
  gap: 16px;
  overflow-x: auto;
}

.similar-item {
  flex-shrink: 0;
  width: 120px;
  cursor: pointer;
  text-align: center;
}

.similar-poster {
  width: 120px;
  height: 170px;
  overflow: hidden;
  border-radius: 6px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.similar-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder-sm {
  color: #c0c4cc;
}

.similar-title {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0;
}

.similar-rating {
  font-size: 12px;
  color: #ff9900;
  margin: 4px 0 0;
}
</style>
