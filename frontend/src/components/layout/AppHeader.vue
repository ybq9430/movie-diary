<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="route.name !== 'Home'">{{ routeTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right" />
  </el-header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const titleMap = {
  Movies: '电影库',
  MovieDetail: '电影详情',
  Stats: '统计分析',
  Import: '数据导入',
  Scrape: '豆瓣抓取',
  Personality: '性格分析',
  Portrait: 'AI 肖像',
  Recommend: '智能推荐',
}
const routeTitle = computed(() => titleMap[route.name] || '')
</script>

<style scoped>
.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
</style>
