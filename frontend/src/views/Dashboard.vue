<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { recommendationsAPI } from '../api'

const loading = ref(true)
const stats = ref({ total_movies: 0, total_ratings: 0, total_users: 0 })

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

const chartTheme = {
  textColor: '#8a8a94',
  axisLine: 'rgba(255,255,255,0.06)',
  accent: '#e8a838',
  accentDim: 'rgba(232,168,56,0.15)',
}

const renderRatingChart = (data) => {
  const chart = echarts.init(ratingChartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c1c22',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#e8e6e1', fontSize: 13 }
    },
    grid: { top: 40, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: data.map(d => `${d.score}分`),
      axisLine: { lineStyle: { color: chartTheme.axisLine } },
      axisLabel: { color: chartTheme.textColor, fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: chartTheme.axisLine } },
      axisLabel: { color: chartTheme.textColor, fontSize: 12 }
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: chartTheme.accent },
          { offset: 1, color: 'rgba(232,168,56,0.3)' }
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      barWidth: '50%',
      emphasis: {
        itemStyle: {
          color: chartTheme.accent,
          shadowBlur: 12,
          shadowColor: 'rgba(232,168,56,0.3)'
        }
      }
    }]
  })
}

const renderGenreChart = (data) => {
  const chart = echarts.init(genreChartRef.value)
  const colors = [
    '#e8a838', '#d4783c', '#b85c3a', '#8a4a38',
    '#6b3d35', '#4d3030', '#e8c068', '#d4a050',
    '#c08840', '#a87030'
  ]
  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1c1c22',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#e8e6e1', fontSize: 13 },
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['42%', '72%'],
      center: ['50%', '55%'],
      data: data.map((d, i) => ({
        name: d.genre,
        value: d.count,
        itemStyle: { color: colors[i % colors.length] }
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 16,
          shadowColor: 'rgba(0,0,0,0.4)'
        }
      },
      label: {
        color: chartTheme.textColor,
        fontSize: 12,
        formatter: '{b}'
      },
      labelLine: {
        lineStyle: { color: 'rgba(255,255,255,0.1)' }
      }
    }]
  })
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="dashboard">
    <div class="dashboard__header animate-fade-in-up">
      <h1 class="dashboard__title">数据看板</h1>
      <p class="dashboard__sub">平台数据概览与统计分析</p>
    </div>

    <!-- Stat Cards -->
    <div v-if="loading" class="stat-grid">
      <div v-for="i in 3" :key="i" class="stat-skeleton">
        <div class="stat-skeleton__icon"></div>
        <div class="stat-skeleton__text"></div>
      </div>
    </div>

    <div v-else class="stat-grid animate-fade-in-up delay-1">
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--film">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="2" y="4" width="20" height="16" rx="3"/>
            <path d="M2 8h20M8 4v16M16 4v16"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__number">{{ stats.total_movies }}</p>
          <p class="stat-card__label">电影总数</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--star">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17l-5.8 3L7.3 13.5 2.6 8.9l6.5-1L12 2z"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__number">{{ stats.total_ratings }}</p>
          <p class="stat-card__label">评分总数</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--user">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__number">{{ stats.total_users }}</p>
          <p class="stat-card__label">活跃用户</p>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div v-if="!loading" class="chart-grid animate-fade-in-up delay-2">
      <div class="chart-card">
        <h3 class="chart-card__title">评分分布</h3>
        <div ref="ratingChartRef" class="chart-card__canvas"></div>
      </div>
      <div class="chart-card">
        <h3 class="chart-card__title">电影类型分布</h3>
        <div ref="genreChartRef" class="chart-card__canvas"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

.dashboard__header {
  margin-bottom: 40px;
}

.dashboard__title {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.dashboard__sub {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}

/* Stat Grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.3s var(--ease-out-expo);
}

.stat-card:hover {
  border-color: var(--border-medium);
  transform: translateY(-2px);
}

.stat-card__icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-card__icon--film {
  background: var(--accent-dim);
  color: var(--accent);
}

.stat-card__icon--star {
  background: rgba(232, 68, 68, 0.12);
  color: #e84444;
}

.stat-card__icon--user {
  background: rgba(68, 200, 120, 0.12);
  color: #44c878;
}

.stat-card__body {
  flex: 1;
}

.stat-card__number {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.stat-card__label {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 4px 0 0;
}

/* Skeleton */
.stat-skeleton {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.stat-skeleton__icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card-hover) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.stat-skeleton__text {
  flex: 1;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card-hover) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* Chart Grid */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.chart-card__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.chart-card__canvas {
  height: 340px;
}

/* Responsive */
@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }

  .chart-card__canvas {
    height: 280px;
  }
}
</style>
