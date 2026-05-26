<template>
  <el-aside :width="ui.sidebarCollapsed ? '64px' : '220px'" class="sidebar">
    <div class="logo">
      <span v-if="!ui.sidebarCollapsed">Movie Diary</span>
      <span v-else>MD</span>
    </div>
    <el-menu
      :default-active="route.path"
      :collapse="ui.sidebarCollapsed"
      router
      class="sidebar-menu"
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      <el-menu-item index="/movies">
        <el-icon><Film /></el-icon>
        <template #title>电影库</template>
      </el-menu-item>
      <el-menu-item index="/stats">
        <el-icon><DataAnalysis /></el-icon>
        <template #title>统计</template>
      </el-menu-item>
      <el-menu-item index="/import">
        <el-icon><Upload /></el-icon>
        <template #title>导入</template>
      </el-menu-item>
      <el-menu-item index="/scrape">
        <el-icon><Download /></el-icon>
        <template #title>抓取</template>
      </el-menu-item>
      <el-sub-menu index="ai">
        <template #title>
          <el-icon><MagicStick /></el-icon>
          <span>AI 功能</span>
        </template>
        <el-menu-item index="/personality">性格分析</el-menu-item>
        <el-menu-item index="/portrait">AI 肖像</el-menu-item>
        <el-menu-item index="/recommend">智能推荐</el-menu-item>
      </el-sub-menu>
    </el-menu>
    <div class="sidebar-toggle" @click="ui.toggleSidebar">
      <el-icon><Fold v-if="!ui.sidebarCollapsed" /><Expand v-else /></el-icon>
    </div>
  </el-aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useUiStore } from '../../stores/ui'

const route = useRoute()
const ui = useUiStore()
</script>

<style scoped>
.sidebar {
  background: #1e1e2d;
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  border-bottom: 1px solid #2d2d3f;
}
.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}
.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}
.sidebar-menu .el-menu-item,
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #a2a3b7;
}
.sidebar-menu .el-menu-item:hover,
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: #2d2d3f;
  color: #fff;
}
.sidebar-menu .el-menu-item.is-active {
  color: #409eff;
  background: #2d2d3f;
}
.sidebar-toggle {
  padding: 12px;
  text-align: center;
  cursor: pointer;
  color: #a2a3b7;
  border-top: 1px solid #2d2d3f;
}
.sidebar-toggle:hover {
  color: #fff;
}
</style>
