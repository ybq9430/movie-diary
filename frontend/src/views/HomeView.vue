<template>
  <div class="home-view">
    <h1 class="page-title">Movie Diary</h1>
    <p class="page-subtitle">我的观影日记</p>

    <!-- Summary Cards -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value">{{ overview.total_movies || 0 }}</div>
          <div class="summary-label">看过电影</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value">{{ overview.avg_rating || '-' }}</div>
          <div class="summary-label">平均评分</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value">{{ overview.favorite_genre || '-' }}</div>
          <div class="summary-label">最爱类型</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="summary-value">{{ overview.time_span || '-' }}</div>
          <div class="summary-label">观影时间</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quick Actions -->
    <el-row :gutter="16" class="action-row">
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/scrape')">
          <el-icon :size="32" color="#f56c6c"><Download /></el-icon>
          <h3>豆瓣抓取</h3>
          <p>输入用户 ID 抓取观影记录</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/import')">
          <el-icon :size="32" color="#409eff"><Upload /></el-icon>
          <h3>导入数据</h3>
          <p>从 CSV 导入观影记录</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/personality')">
          <el-icon :size="32" color="#e6a23c"><MagicStick /></el-icon>
          <h3>AI 性格分析</h3>
          <p>了解你的观影性格</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="action-card" @click="$router.push('/movies')">
          <el-icon :size="32" color="#67c23a"><Film /></el-icon>
          <h3>电影库</h3>
          <p>浏览所有电影</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Movies -->
    <h2 class="section-title">最近观看</h2>
    <el-row :gutter="16">
      <el-col v-for="movie in recentMovies" :key="movie.id" :xs="12" :sm="8" :md="6" :lg="4">
        <MovieCard :movie="movie" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOverview } from '../api/stats'
import { getMovies } from '../api/movie'
import MovieCard from '../components/movie/MovieCard.vue'

const overview = ref({})
const recentMovies = ref([])

onMounted(async () => {
  const [ov, movies] = await Promise.allSettled([
    getOverview(),
    getMovies({ page: 1, per_page: 12, sort_by: 'watch_date', sort_order: 'desc' }),
  ])
  if (ov.status === 'fulfilled') overview.value = ov.value
  if (movies.status === 'fulfilled') recentMovies.value = movies.value.items || []
})
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}
.page-subtitle {
  color: #909399;
  margin-bottom: 24px;
}
.summary-row {
  margin-bottom: 24px;
}
.summary-card {
  text-align: center;
  padding: 8px 0;
}
.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}
.summary-label {
  color: #909399;
  margin-top: 4px;
}
.action-row {
  margin-bottom: 32px;
}
.action-card {
  text-align: center;
  cursor: pointer;
  padding: 20px;
}
.action-card h3 {
  margin: 12px 0 4px;
  color: #303133;
}
.action-card p {
  color: #909399;
  font-size: 13px;
}
.section-title {
  font-size: 20px;
  margin-bottom: 16px;
  color: #303133;
}
</style>
