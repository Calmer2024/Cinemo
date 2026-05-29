<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ratingsAPI } from '../api'

const router = useRouter()
const ratings = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)

const fetchRatings = async () => {
  loading.value = true
  try {
    const res = await ratingsAPI.getByUser({ page: page.value, per_page: 20 })
    ratings.value = res.ratings
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const deleteRating = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除这条评分吗？', '确认')
    await ratingsAPI.delete(id)
    ElMessage.success('删除成功')
    fetchRatings()
  } catch {}
}

onMounted(fetchRatings)
</script>

<template>
  <div class="my-ratings">
    <div class="my-ratings__header animate-fade-in-up">
      <h1 class="my-ratings__title">我的评分</h1>
      <p class="my-ratings__sub">管理你的电影评分记录</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="ratings-list">
      <div v-for="i in 5" :key="i" class="rating-skeleton">
        <div class="rating-skeleton__left">
          <div class="rating-skeleton__bar"></div>
        </div>
        <div class="rating-skeleton__right">
          <div class="rating-skeleton__bar rating-skeleton__bar--short"></div>
        </div>
      </div>
    </div>

    <!-- Ratings List -->
    <div v-else-if="ratings.length > 0" class="ratings-list animate-fade-in-up delay-1">
      <article
        v-for="r in ratings"
        :key="r.id"
        class="rating-item"
      >
        <div class="rating-item__left">
          <div class="rating-item__stars">
            <svg v-for="i in 5" :key="i" width="16" height="16" viewBox="0 0 14 14"
              :fill="i <= r.score ? 'var(--accent)' : 'var(--text-tertiary)'">
              <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
            </svg>
          </div>
          <p v-if="r.review" class="rating-item__review">{{ r.review }}</p>
          <p class="rating-item__date">{{ new Date(r.created_at).toLocaleDateString() }}</p>
        </div>
        <div class="rating-item__right">
          <button class="rating-item__detail" @click="router.push(`/movie/${r.movie_id}`)">查看电影</button>
          <button class="rating-item__delete" @click="deleteRating(r.id)">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 4h10M6 4V3a1 1 0 011-1h2a1 1 0 011 1v1M5 4v8a1 1 0 001 1h4a1 1 0 001-1V4" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </article>
    </div>

    <!-- Empty -->
    <div v-else class="empty-state animate-fade-in">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <path d="M32 8l5.9 12 13.2 1.9-9.6 9.3 2.3 13.1L32 38.5l-11.8 5.8 2.3-13.1-9.6-9.3 13.2-1.9L32 8z" stroke="currentColor" stroke-width="2" opacity="0.3"/>
      </svg>
      <p>还没有评分记录</p>
      <button class="btn btn--accent" @click="router.push('/')">去发现电影</button>
    </div>

    <!-- Pagination -->
    <div v-if="total > 20" class="pagination-wrap">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="20"
        :current-page="page"
        @current-change="(p) => { page = p; fetchRatings() }"
      />
    </div>
  </div>
</template>

<style scoped>
.my-ratings {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

.my-ratings__header {
  margin-bottom: 36px;
}

.my-ratings__title {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.my-ratings__sub {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}

/* Ratings List */
.ratings-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.rating-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 0;
  border-bottom: 1px solid var(--border-subtle);
  gap: 20px;
  transition: background 0.2s ease;
}

.rating-item:last-child {
  border-bottom: none;
}

.rating-item__left {
  flex: 1;
  min-width: 0;
}

.rating-item__stars {
  display: flex;
  gap: 2px;
  margin-bottom: 8px;
}

.rating-item__review {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 6px;
}

.rating-item__date {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.rating-item__right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.rating-item__detail {
  padding: 6px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rating-item__detail:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.rating-item__delete {
  padding: 6px;
  background: none;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  transition: all 0.2s ease;
}

.rating-item__delete:hover {
  color: #e84444;
  border-color: rgba(232, 68, 68, 0.2);
  background: rgba(232, 68, 68, 0.08);
}

/* Skeleton */
.rating-skeleton {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.rating-skeleton__bar {
  height: 16px;
  width: 200px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card-hover) 50%, var(--bg-elevated) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.rating-skeleton__bar--short {
  width: 80px;
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

/* Pagination */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 640px) {
  .rating-item {
    flex-direction: column;
    gap: 12px;
  }

  .rating-item__right {
    align-self: flex-end;
  }
}
</style>
