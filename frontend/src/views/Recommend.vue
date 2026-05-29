<script setup>
import { ref, onMounted } from 'vue'
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
  } finally {
    loading.value = false
  }
}

const triggerSpark = async () => {
  triggering.value = true
  try {
    const res = await recommendationsAPI.trigger()
    ElMessage.success('推荐计算完成')
    fetchRecommendations()
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    triggering.value = false
  }
}

onMounted(fetchRecommendations)
</script>

<template>
  <div class="recommend-page">
    <div class="page-header">
      <h2>个性化推荐</h2>
      <el-button type="primary" :loading="triggering" @click="triggerSpark">
        <el-icon><Refresh /></el-icon>
        重新计算推荐
      </el-button>
    </div>

    <p class="intro">
      基于 Spark ALS 协同过滤算法，根据您的评分历史为您推荐可能喜欢的电影。
    </p>

    <div v-loading="loading" class="recommend-grid">
      <el-card
        v-for="rec in recommendations"
        :key="rec.id"
        class="rec-card"
        @click="router.push(`/movie/${rec.movie_id}`)"
        shadow="hover"
      >
        <div class="rec-poster">
          <img v-if="rec.movie?.poster_url" :src="rec.movie.poster_url" />
          <div v-else class="poster-placeholder"><el-icon :size="40"><Film /></el-icon></div>
          <div class="rec-score">
            预测 {{ rec.score.toFixed(1) }}
          </div>
        </div>
        <div class="rec-info">
          <h4>{{ rec.movie?.title }}</h4>
          <p>{{ rec.movie?.year }} · {{ rec.movie?.genres?.join(' / ') }}</p>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && recommendations.length === 0" description="暂无推荐，请先对一些电影评分后再来">
      <el-button type="primary" @click="router.push('/')">去评分</el-button>
    </el-empty>
  </div>
</template>

<style scoped>
.recommend-page {
  padding-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.page-header h2 {
  margin: 0;
}

.intro {
  color: #909399;
  margin-bottom: 20px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.rec-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.rec-card:hover {
  transform: translateY(-4px);
}

.rec-poster {
  position: relative;
  width: 100%;
  height: 250px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  color: #c0c4cc;
}

.rec-score {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(103, 126, 234, 0.9);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.rec-info {
  padding: 10px 0 0;
}

.rec-info h4 {
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rec-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
</style>
