<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { recommendationsAPI } from '../api'

const loading = ref(true)
const stats = ref({
  total_movies: 0,
  total_ratings: 0,
  total_users: 0
})

const ratingChartRef = ref(null)
const genreChartRef = ref(null)

const fetchDashboard = async () => {
  loading.value = true
  try {
    const res = await recommendationsAPI.dashboard()
    stats.value = {
      total_movies: res.total_movies,
      total_ratings: res.total_ratings,
      total_users: res.total_users
    }

    await nextTick()
    renderRatingChart(res.rating_distribution)
    renderGenreChart(res.genre_distribution)
  } finally {
    loading.value = false
  }
}

const renderRatingChart = (data) => {
  const chart = echarts.init(ratingChartRef.value)
  const scores = data.map(d => `${d.score}分`)
  const counts = data.map(d => d.count)

  chart.setOption({
    title: { text: '评分分布', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: scores,
      axisLabel: { fontSize: 13 }
    },
    yAxis: { type: 'value', name: '数量' },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '40%'
    }]
  })
}

const renderGenreChart = (data) => {
  const chart = echarts.init(genreChartRef.value)
  chart.setOption({
    title: { text: '电影类型分布 (Top 10)', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '55%'],
      data: data.map(d => ({ name: d.genre, value: d.count })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      },
      label: { fontSize: 13 }
    }]
  })
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="dashboard" v-loading="loading">
    <h2>数据看板</h2>

    <!-- 统计卡片 -->
    <div class="stat-cards">
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #667eea"><el-icon :size="28"><Film /></el-icon></div>
        <div class="stat-info">
          <p class="stat-number">{{ stats.total_movies }}</p>
          <p class="stat-label">电影总数</p>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #f56c6c"><el-icon :size="28"><Star /></el-icon></div>
        <div class="stat-info">
          <p class="stat-number">{{ stats.total_ratings }}</p>
          <p class="stat-label">评分总数</p>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #67c23a"><el-icon :size="28"><User /></el-icon></div>
        <div class="stat-info">
          <p class="stat-number">{{ stats.total_users }}</p>
          <p class="stat-label">活跃用户</p>
        </div>
      </el-card>
    </div>

    <!-- 图表 -->
    <div class="chart-row">
      <el-card class="chart-card">
        <div ref="ratingChartRef" class="chart"></div>
      </el-card>
      <el-card class="chart-card">
        <div ref="genreChartRef" class="chart"></div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.dashboard h2 {
  margin-bottom: 20px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  width: 100%;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 0;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin: 4px 0 0;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart {
  height: 360px;
}
</style>
