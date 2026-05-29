<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../api'

const router = useRouter()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await authAPI.login(form.value)
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-page__bg">
      <div class="auth-page__gradient"></div>
    </div>

    <div class="auth-card animate-fade-in-up">
      <div class="auth-card__header">
        <div class="auth-card__logo">
          <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="4" width="24" height="20" rx="4" stroke="currentColor" stroke-width="2"/>
            <circle cx="10" cy="14" r="3" fill="currentColor"/>
            <circle cx="18" cy="14" r="3" fill="currentColor"/>
          </svg>
        </div>
        <h1 class="auth-card__title">欢迎回来</h1>
        <p class="auth-card__sub">登录你的 Cinemo 账号</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="auth-field">
          <label class="auth-field__label">用户名</label>
          <input
            v-model="form.username"
            type="text"
            class="auth-field__input"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>
        <div class="auth-field">
          <label class="auth-field__label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="auth-field__input"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>
        <button
          type="submit"
          class="btn btn--accent btn--full"
          :class="{ 'btn--loading': loading }"
          :disabled="loading"
        >
          <span v-if="loading" class="btn__spinner"></span>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="auth-card__footer">
        还没有账号？
        <router-link to="/register" class="auth-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 72px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  position: relative;
}

.auth-page__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.auth-page__gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(232, 168, 56, 0.06), transparent),
    var(--bg-primary);
}

.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 40px 36px;
}

.auth-card__header {
  text-align: center;
  margin-bottom: 36px;
}

.auth-card__logo {
  color: var(--accent);
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.auth-card__title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.auth-card__sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 28px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-field__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.auth-field__input {
  padding: 12px 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s ease;
}

.auth-field__input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.auth-field__input::placeholder {
  color: var(--text-tertiary);
}

.btn--full {
  width: 100%;
  padding: 14px;
  font-size: 15px;
  margin-top: 8px;
  position: relative;
}

.btn--loading {
  opacity: 0.8;
  cursor: not-allowed;
}

.btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-card__footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-link {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.auth-link:hover {
  opacity: 0.8;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 32px 24px;
  }
}
</style>
