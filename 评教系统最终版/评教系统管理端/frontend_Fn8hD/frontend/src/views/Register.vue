<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo 和标题 -->
      <div class="login-header">
        <div class="logo-container">
          <img src="../images/school-logo.jpg" alt="广西警察学院" class="school-logo" />
        </div>
        <h1 class="login-title">教研室数据管理平台</h1>
      </div>

      <!-- 注册表单 -->
      <form class="login-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            v-model="registerForm.username"
            type="text"
            class="form-input"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="registerForm.email"
            type="email"
            class="form-input"
            placeholder="请输入邮箱"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label class="form-label">姓名</label>
          <input
            v-model="registerForm.full_name"
            type="text"
            class="form-input"
            placeholder="请输入姓名"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="password-input-wrapper">
            <input
              v-model="registerForm.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入密码"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">确认密码</label>
          <div class="password-input-wrapper">
            <input
              v-model="registerForm.confirm_password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请再次输入密码"
              required
              autocomplete="new-password"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">验证码</label>
          <div class="captcha-wrapper">
            <input
              v-model="registerForm.captcha"
              type="text"
              class="form-input captcha-input"
              placeholder="请输入验证码"
              required
              maxlength="6"
            />
            <div class="captcha-image-container">
              <img
                :src="captchaImageUrl"
                alt="验证码"
                class="captcha-image"
                @click="refreshCaptcha"
                title="点击刷新验证码"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          class="btn-login"
          :disabled="loading"
        >
          <span v-if="!loading">注册</span>
          <span v-else class="loading-text">
            <span class="loading-spinner"></span>
            注册中...
          </span>
        </button>

        <div class="register-link">
          已有账号？
          <a href="#" @click.prevent="$emit('switch-to-login')">立即登录</a>
        </div>
      </form>
    </div>

    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const emit = defineEmits(['switch-to-login']);

const registerForm = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirm_password: '',
  captcha: ''
});

const showPassword = ref(false);
const loading = ref(false);
// 模拟验证码实现
const captchaImageUrl = ref('');
const captchaCode = ref('');

// 生成随机验证码
const generateCaptchaCode = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
};

// 生成验证码图片（使用Canvas模拟）
const generateCaptchaImage = () => {
  const code = generateCaptchaCode();
  captchaCode.value = code;
  
  // 创建Canvas
  const canvas = document.createElement('canvas');
  canvas.width = 120;
  canvas.height = 40;
  const ctx = canvas.getContext('2d');
  
  if (ctx) {
    // 设置背景
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制验证码
    ctx.font = '20px Arial';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(code, canvas.width / 2, canvas.height / 2);
    
    // 添加干扰线
    ctx.strokeStyle = '#ccc';
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.stroke();
    }
    
    // 添加噪点
    ctx.fillStyle = '#999';
    for (let i = 0; i < 50; i++) {
      ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 1, 1);
    }
    
    // 转换为DataURL
    captchaImageUrl.value = canvas.toDataURL('image/png');
  }
};

// 初始化验证码
const refreshCaptcha = () => {
  generateCaptchaImage();
};

// 组件挂载时初始化验证码
onMounted(() => {
  refreshCaptcha();
});

const handleRegister = async () => {
  loading.value = true;
  
  try {
    // 验证验证码
    if (registerForm.value.captcha.toLowerCase() !== captchaCode.value.toLowerCase()) {
      alert('验证码错误，请重新输入');
      refreshCaptcha();
      return;
    }
    
    const apiBaseUrl = 'http://localhost:8001/api';
    // 移除 captcha 字段，因为后端不需要
    const { captcha, ...registerData } = registerForm.value;
    console.log('注册请求数据:', registerData);
    console.log('注册请求URL:', `${apiBaseUrl}/register`);
    const response = await fetch(`${apiBaseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(registerData)
    });
    
    console.log('注册响应状态:', response.status);
    console.log('注册响应状态文本:', response.statusText);
    
    let data;
    try {
      data = await response.json();
      console.log('注册响应数据:', data);
    } catch (error) {
      console.error('解析响应数据失败:', error);
      alert('网络错误，请稍后重试');
      refreshCaptcha();
      return;
    }
    
    if (response.ok) {
      // 显示成功消息
      alert('注册成功！请登录');
      
      // 切换到登录页面
      emit('switch-to-login');
    } else {
      // 正确处理后端返回的错误信息
      let errorMessage = '注册失败，请检查输入信息';
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          // 处理 Pydantic 验证错误数组
          errorMessage = data.detail.map(item => item.msg).join('\n');
        } else {
          // 处理单个错误消息
          errorMessage = data.detail;
        }
      } else if (data.message) {
        // 处理其他错误消息格式
        errorMessage = data.message;
      } else {
        // 处理其他错误消息格式
        errorMessage = JSON.stringify(data);
      }
      console.log('错误消息:', errorMessage);
      alert(errorMessage);
      // 刷新验证码
      refreshCaptcha();
    }
  } catch (error) {
    console.error('注册错误:', error);
    alert('网络错误，请稍后重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
:global(html),
:global(body) {
  margin: 0;
  padding: 0;
  min-height: 100%;
  width: 100%;
  overflow-x: hidden;
}

.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #003366;
  padding: 20px;
  position: relative;
  margin: 0;
}

.login-card {
  width: 100%;
  max-width: 460px;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 40px 32px;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.5s ease;
  border: 1px solid #E0E0E0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #F0F0F0;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.school-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 4px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #003366;
  margin: 0 0 8px 0;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.login-subtitle {
  font-size: 14px;
  color: #666666;
  margin: 0;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #333333;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  font-size: 14px;
  color: #333333;
  background: #FFFFFF;
  border: 1px solid #D0D0D0;
  border-radius: 4px;
  transition: all 0.2s ease;
  outline: none;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.form-input:hover {
  border-color: #003366;
  background: #FAFAFA;
}

.form-input:focus {
  border-color: #003366;
  background: #FFFFFF;
  box-shadow: 0 0 0 2px rgba(0, 51, 102, 0.1);
}

.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.password-toggle:hover {
  opacity: 1;
}

/* 验证码样式 */
.captcha-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image-container {
  display: flex;
  align-items: center;
}

.captcha-image {
  width: 110px;
  height: 40px;
  border-radius: 4px;
  cursor: pointer;
  object-fit: cover;
  border: 1px solid #D0D0D0;
  transition: border-color 0.2s ease;
}

.captcha-image:hover {
  border-color: #003366;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666666;
  cursor: pointer;
  user-select: none;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.checkbox-label input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
  accent-color: #003366;
}

.forgot-link {
  font-size: 13px;
  color: #003366;
  text-decoration: none;
  transition: color 0.2s ease;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.forgot-link:hover {
  color: #004080;
  text-decoration: underline;
}

.btn-login {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  font-weight: 500;
  color: #FFFFFF;
  background: #003366;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 12px;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.btn-login:hover:not(:disabled) {
  background: #004080;
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.2);
}

.btn-login:active:not(:disabled) {
  background: #00264d;
}

.btn-login:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.register-link {
  text-align: center;
  font-size: 13px;
  color: #666666;
  margin-top: 16px;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.register-link a {
  color: #003366;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.register-link a:hover {
  color: #004080;
  text-decoration: underline;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  animation: float-circle 20s ease-in-out infinite;
}

.circle-1 {
  width: 150px;
  height: 150px;
  top: -75px;
  right: -75px;
}

.circle-2 {
  width: 100px;
  height: 100px;
  bottom: -50px;
  left: -50px;
  animation-delay: -5s;
}

.circle-3 {
  width: 80px;
  height: 80px;
  top: 50%;
  left: 10%;
  animation-delay: -10s;
}

@keyframes float-circle {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(15px, -15px) scale(1.1);
  }
  66% {
    transform: translate(-10px, 10px) scale(0.9);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-card {
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .login-card {
    padding: 40px 32px;
  }
  
  .captcha-wrapper {
    flex-direction: column;
    align-items: stretch;
  }
  
  .captcha-image-container {
    justify-content: center;
  }
  
  .captcha-image {
    width: 100%;
    max-width: 150px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    max-width: 100%;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .checkbox-label {
    justify-content: center;
  }
  
  .forgot-link {
    text-align: center;
  }
}
</style>
