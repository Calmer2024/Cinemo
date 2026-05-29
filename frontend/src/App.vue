<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const user = ref(null)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const scrolled = ref(false)
const mobileMenuOpen = ref(false)
const showUserCard = ref(false)

onMounted(() => {
  loadUser()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('storage', loadUser)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('storage', loadUser)
  document.removeEventListener('click', handleClickOutside)
})

const loadUser = () => {
  const saved = localStorage.getItem('user')
  if (saved) {
    try { user.value = JSON.parse(saved) } catch { user.value = null }
  } else {
    user.value = null
  }
}

// 监听路由变化，刷新用户状态
router.afterEach(() => {
  loadUser()
})

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
}

const handleClickOutside = (e) => {
  const card = document.querySelector('.user-card')
  const trigger = document.querySelector('.nav__user')
  if (card && !card.contains(e.target) && trigger && !trigger.contains(e.target)) {
    showUserCard.value = false
  }
}

const toggleUserCard = () => {
  showUserCard.value = !showUserCard.value
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  showUserCard.value = false
  ElMessage.success('已退出登录')
  router.push('/')
}

const activeMenu = computed(() => route.path)

const navItems = computed(() => {
  const items = [
    { path: '/', label: '发现', icon: 'discover' },
    { path: '/dashboard', label: '数据', icon: 'chart' },
  ]
  if (isLoggedIn.value) {
    items.push({ path: '/recommend', label: '推荐', icon: 'magic' })
    items.push({ path: '/my-ratings', label: '我的', icon: 'star' })
  }
  return items
})
</script>

<template>
  <div class="app-shell">
    <!-- Navigation -->
    <header class="nav" :class="{ 'nav--scrolled': scrolled }">
      <div class="nav__inner">
        <div class="nav__brand" @click="router.push('/')">
          <div class="nav__logo">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect x="2" y="4" width="24" height="20" rx="4" stroke="currentColor" stroke-width="2"/>
              <circle cx="10" cy="14" r="3" fill="currentColor"/>
              <circle cx="18" cy="14" r="3" fill="currentColor"/>
              <path d="M2 8h24" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
            </svg>
          </div>
          <span class="nav__brand-text">Cinemo</span>
        </div>

        <nav class="nav__links">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav__link"
            :class="{ 'nav__link--active': activeMenu === item.path }"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <div class="nav__actions">
          <template v-if="isLoggedIn && user">
            <div class="nav__user" @click.stop="toggleUserCard">
              <div class="nav__avatar">
                {{ user.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <span class="nav__username">{{ user.username || '用户' }}</span>
              <svg class="nav__chevron" :class="{ 'is-open': showUserCard }" width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3.5 5.5L7 9l3.5-3.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <!-- User Card Dropdown -->
            <transition name="card-drop">
              <div v-if="showUserCard" class="user-card" @click.stop>
                <div class="user-card__header">
                  <div class="user-card__avatar">
                    {{ user.username?.charAt(0)?.toUpperCase() || 'U' }}
                  </div>
                  <div class="user-card__info">
                    <p class="user-card__name">{{ user.username }}</p>
                    <p class="user-card__email">{{ user.email }}</p>
                  </div>
                </div>
                <div class="user-card__divider"></div>
                <div class="user-card__stats">
                  <div class="user-card__stat">
                    <svg width="16" height="16" viewBox="0 0 14 14" fill="currentColor">
                      <path d="M7 1l1.76 3.57L13 5.24l-3 2.92.71 4.13L7 10.27 3.29 12.3 4 8.16l-3-2.92 4.24-.67L7 1z"/>
                    </svg>
                    <span>我的评分</span>
                  </div>
                  <div class="user-card__stat">
                    <svg width="16" height="16" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.3">
                      <circle cx="7" cy="7" r="5.5"/>
                      <path d="M7 4v3l2 1.5" stroke-linecap="round"/>
                    </svg>
                    <span>最近活跃</span>
                  </div>
                </div>
                <div class="user-card__divider"></div>
                <button class="user-card__logout" @click="handleLogout">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M6 2H4a2 2 0 00-2 2v8a2 2 0 002 2h2M11 11l3-3-3-3M14 8H6" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  退出登录
                </button>
              </div>
            </transition>
          </template>
          <template v-else>
            <button class="btn btn--ghost" @click="router.push('/login')">登录</button>
            <button class="btn btn--accent" @click="router.push('/register')">注册</button>
          </template>
        </div>

        <!-- Mobile menu toggle -->
        <button class="nav__mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
          <span :class="{ 'is-open': mobileMenuOpen }"></span>
        </button>
      </div>

      <!-- Mobile menu -->
      <transition name="slide-down">
        <div v-if="mobileMenuOpen" class="nav__mobile-menu">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav__mobile-link"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </router-link>
          <div class="nav__mobile-actions">
            <template v-if="isLoggedIn && user">
              <div class="mobile-user-info">
                <div class="nav__avatar">{{ user.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
                <div>
                  <p class="mobile-user-name">{{ user.username }}</p>
                  <p class="mobile-user-email">{{ user.email }}</p>
                </div>
              </div>
              <button class="btn btn--ghost" style="width:100%" @click="handleLogout; mobileMenuOpen = false">退出登录</button>
            </template>
            <template v-else>
              <button class="btn btn--ghost" style="width:100%" @click="router.push('/login'); mobileMenuOpen = false">登录</button>
              <button class="btn btn--accent" style="width:100%" @click="router.push('/register'); mobileMenuOpen = false">注册</button>
            </template>
          </div>
        </div>
      </transition>
    </header>

    <!-- Main Content -->
    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer__inner">
        <div class="footer__brand">
          <span class="footer__logo">Cinemo</span>
          <span class="footer__sep">-</span>
          <span class="footer__tagline">智能电影推荐系统</span>
        </div>
        <p class="footer__copy">武汉大学计算机学院 - 云计算平台与技术课程</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* --- Navigation --- */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0 24px;
  transition: all 0.3s var(--ease-out-expo);
  background: transparent;
}

.nav--scrolled {
  background: rgba(10, 10, 12, 0.95);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.05);
}

.nav__inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}

.nav__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.nav__brand:hover {
  opacity: 0.8;
}

.nav__logo {
  color: var(--accent);
  display: flex;
}

.nav__brand-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.nav__links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav__link {
  padding: 8px 16px;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
}

.nav__link:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
  opacity: 1;
}

.nav__link--active {
  color: var(--accent);
  background: var(--accent-dim);
}

.nav__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.nav__user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px 6px 6px;
  border-radius: var(--radius-pill);
  transition: background 0.2s ease;
  user-select: none;
}

.nav__user:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--text-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.nav__username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.nav__chevron {
  color: var(--text-tertiary);
  transition: transform 0.2s ease;
}

.nav__chevron.is-open {
  transform: rotate(180deg);
}

/* --- User Card Dropdown --- */
.user-card {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 260px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  z-index: 200;
}

.user-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.user-card__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--text-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-card__info {
  flex: 1;
  min-width: 0;
}

.user-card__name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2px;
}

.user-card__email {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card__divider {
  height: 1px;
  background: var(--border-subtle);
}

.user-card__stats {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-card__stat {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
}

.user-card__stat:hover {
  color: var(--accent);
}

.user-card__logout {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  font-size: 13px;
  font-family: inherit;
  color: #e84444;
  cursor: pointer;
  transition: background 0.2s ease;
}

.user-card__logout:hover {
  background: rgba(232, 68, 68, 0.08);
}

/* Card drop animation */
.card-drop-enter-active {
  animation: cardDropIn 0.2s var(--ease-out-expo);
}

.card-drop-leave-active {
  animation: cardDropIn 0.15s ease reverse;
}

@keyframes cardDropIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Mobile user info */
.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.mobile-user-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.mobile-user-email {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 2px 0 0;
}

/* --- Buttons --- */
.btn {
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: none;
  transition: all 0.2s var(--ease-out-expo);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn--accent {
  background: var(--accent);
  color: var(--text-on-accent);
}

.btn--accent:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}

.btn--accent:active {
  transform: translateY(0);
}

.btn--ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
}

.btn--ghost:hover {
  color: var(--text-primary);
  border-color: var(--accent);
}

/* --- Main Content --- */
.main {
  min-height: 100vh;
  padding-top: 72px;
}

/* --- Footer --- */
.footer {
  border-top: 1px solid var(--border-subtle);
  padding: 40px 24px;
  margin-top: var(--section-gap);
}

.footer__inner {
  max-width: 1280px;
  margin: 0 auto;
  text-align: center;
}

.footer__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
}

.footer__logo {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.footer__sep {
  color: var(--text-tertiary);
}

.footer__tagline {
  font-size: 14px;
  color: var(--text-secondary);
}

.footer__copy {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

/* --- Page Transitions --- */
.page-enter-active {
  animation: fadeInUp 0.4s var(--ease-out-expo);
}

.page-leave-active {
  animation: fadeIn 0.2s ease reverse;
}

.slide-down-enter-active {
  animation: fadeInUp 0.3s var(--ease-out-expo);
}

.slide-down-leave-active {
  animation: fadeIn 0.2s ease reverse;
}

/* --- Responsive --- */
@media (max-width: 768px) {
  .nav__links,
  .nav__actions {
    display: none;
  }

  .nav__mobile-toggle {
    display: block;
  }

  .nav__mobile-menu {
    display: flex;
  }

  .nav__inner {
    height: 60px;
  }

  .main {
    padding-top: 60px;
  }
}

.nav__mobile-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  position: relative;
}

.nav__mobile-toggle span,
.nav__mobile-toggle span::before,
.nav__mobile-toggle span::after {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 2px;
  transition: all 0.3s ease;
  position: absolute;
  left: 6px;
}

.nav__mobile-toggle span { top: 15px; }
.nav__mobile-toggle span::before { content: ''; top: -6px; }
.nav__mobile-toggle span::after { content: ''; top: 6px; }

.nav__mobile-toggle span.is-open { background: transparent; }
.nav__mobile-toggle span.is-open::before { top: 0; transform: rotate(45deg); }
.nav__mobile-toggle span.is-open::after { top: 0; transform: rotate(-45deg); }

.nav__mobile-menu {
  display: none;
  flex-direction: column;
  gap: 4px;
  padding: 16px 0 24px;
  border-top: 1px solid var(--border-subtle);
}

.nav__mobile-link {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav__mobile-link:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
  opacity: 1;
}

.nav__mobile-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}
</style>
