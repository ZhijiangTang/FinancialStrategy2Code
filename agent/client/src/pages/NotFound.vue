<template>
  <div class="not-found-container">
    <h1>404</h1>
    <p>页面未找到</p>
    <p>您访问的页面不存在，请检查 URL 或返回首页。</p>
    <router-link to="/main" class="home-link">返回首页</router-link>
  </div>
</template>

<script setup>
defineOptions({
  name: 'NotFound'
})
</script>

<style scoped>
.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background-color: #f8f9fa;
  color: #343a40;
}

h1 {
  font-size: 6rem;
  margin: 0;
  color: #dc3545;
}

p {
  font-size: 1.5rem;
  margin: 10px 0;
}

.home-link {
  margin-top: 20px;
  font-size: 1.2rem;
  color: #007bff;
  text-decoration: none;
}

.home-link:hover {
  text-decoration: underline;
}
</style>
