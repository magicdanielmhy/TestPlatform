<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="logo">测试平台</div>
      <el-menu :default-active="$route.path" router>
        <el-menu-item index="/test-cases">测试用例</el-menu-item>
        <el-menu-item index="/test-case-sets">测试案例集</el-menu-item>
        <el-menu-item index="/executions">执行结果</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>自动化测试平台</span>
        <el-button link type="primary" @click="logout">退出登录</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #001529;
}
.logo {
  color: #fff;
  text-align: center;
  line-height: 60px;
  font-size: 18px;
  font-weight: bold;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
}
</style>
