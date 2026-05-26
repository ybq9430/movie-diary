<template>
  <el-container class="app-container">
    <AppSidebar />
    <el-container>
      <AppHeader />
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppSidebar from './components/layout/AppSidebar.vue'
import AppHeader from './components/layout/AppHeader.vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
}
.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
