import { createRouter, createWebHashHistory } from 'vue-router'
import Main from '../pages/Main.vue'
import NotFound from '../pages/NotFound.vue'
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/main' },
    { path: '/main', component: Main, name: 'main' },
    { path: '/:pathMatch(.*)', component: NotFound, name: 'notFound' }
  ]
})
router.beforeEach(async (to, from, next) => {
  // 在进入路由之前执行的逻辑
  // 如果用户已登录，则允许访问
  next()
})
export default router
