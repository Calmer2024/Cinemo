<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const user = ref(null)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

onMounted(() => {
  const saved = localStorage.getItem('user')
  if (saved) user.value = JSON.parse(saved)
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  ElMessage.success('已退出登录')
  router.push('/')
}

const activeMenu = computed(() => route.path)
</script>

<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo" @click="router.push('/')">
          <el-icon><Film /></el-icon>
          <span>电影推荐系统</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          class="nav-menu"
          router
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item v-if="isLoggedIn" index="/recommend">
            <el-icon><MagicStick /></el-icon>
            <span>个性推荐</span>
          </el-menu-item>
          <el-menu-item v-if="isLoggedIn" index="/my-ratings">
            <el-icon><Star /></el-icon>
            <span>我的评分</span>
          </el-menu-item>
        </el-menu>

        <div class="header-actions">
          <template v-if="isLoggedIn">
            <el-dropdown @command="handleLogout">
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                <span class="username">{{ user?.username || '用户' }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="router.push('/login')">登录</el-button>
            <el-button @click="router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="app-main">
      <router-view />
    </el-main>

    <!-- 底部 -->
    <el-footer class="app-footer">
      <p>云计算课程大作业 - 电影推荐系统 | 武汉大学计算机学院</p>
    </el-footer>
  </el-container>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px !important;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  margin-right: 40px;
  white-space: nowrap;
}

.logo .el-icon {
  font-size: 24px;
}

.nav-menu {
  flex: 1;
  background: transparent !important;
  border: none !important;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.85) !important;
  border-bottom: none !important;
  height: 60px;
  line-height: 60px;
}

.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  color: #fff !important;
  background: rgba(255, 255, 255, 0.15) !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  cursor: pointer;
}

.username {
  font-size: 14px;
}

.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 24px 20px;
}

.app-footer {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 16px;
  background: #f5f7fa;
}
</style>
