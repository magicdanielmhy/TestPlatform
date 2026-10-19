import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Login from '../views/Login.vue'
import Layout from '../views/Layout.vue'
import TestCases from '../views/TestCases.vue'
import TestCaseSets from '../views/TestCaseSets.vue'
import Executions from '../views/Executions.vue'

const routes = [
  { path: '/login', component: Login },
  {
    path: '/',
    component: Layout,
    redirect: '/test-cases',
    children: [
      { path: 'test-cases', component: TestCases },
      { path: 'test-case-sets', component: TestCaseSets },
      { path: 'executions', component: Executions }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.token) return '/login'
  if (to.path === '/login' && auth.token) return '/'
})

export default router
