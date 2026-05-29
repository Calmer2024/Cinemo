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

onMounted(() => {
  const saved = localStorage.getItem('user')
  if (saved) user.value = JSON.parse(saved)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
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
          <template v-if="isLoggedIn">
            <div class="nav__user" @click="handleLogout">
              <div class="nav__avatar">
                {{ user?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <span class="nav__username">{{ user?.username || '用户' }}</span>
            </div>
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
            <template v-if="isLoggedIn">
              <button class="btn btn--ghost" style="width:100%" @click="handleLogout">退出登录</button>
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
  background: rgba(10, 10, 12, 0.85);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  border-bottom: 1px solid var(--border-subtle);
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
}

.nav__user {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px 6px 6px;
  border-radius: var(--radius-pill);
  transition: background 0.2s ease;
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
}

.nav__username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
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
</style>
