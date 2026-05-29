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
    <h2>我的评分</h2>

    <div v-loading="loading">
      <el-table :data="ratings" stripe style="width: 100%">
        <el-table-column label="电影" min-width="200">
          <template #default="{ row }">
            <span class="movie-link" @click="router.push(`/movie/${row.movie_id}`)">
              {{ row.movie_id }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="180">
          <template #default="{ row }">
            <el-rate :model-value="row.score" disabled />
          </template>
        </el-table-column>
        <el-table-column label="评价" prop="review" min-width="200" />
        <el-table-column label="时间" width="120">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" text @click="deleteRating(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && ratings.length === 0" description="暂无评分记录">
        <el-button type="primary" @click="router.push('/')">去评分</el-button>
      </el-empty>

      <div class="pagination" v-if="total > 20">
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
  </div>
</template>

<style scoped>
.my-ratings h2 {
  margin-bottom: 20px;
}

.movie-link {
  color: #409eff;
  cursor: pointer;
}

.movie-link:hover {
  text-decoration: underline;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
