<template>
  <div class="auth-wrapper">
    <transition name="slide-fade" mode="out-in">
      <Login v-if="currentView === 'login'" @switch-to-register="currentView = 'register'" />
      <Register v-else @switch-to-login="currentView = 'login'" />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Login from './Login.vue';
import Register from './Register.vue';

const currentView = ref<'login' | 'register'>('login');
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
}

/* 切换动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>
