<template>
  <el-card class="movie-card" shadow="hover" @click="$router.push(`/movies/${movie.id}`)">
    <div class="card-poster">
      <img
        v-if="posterUrl"
        :src="posterUrl"
        :alt="movie.title"
        class="poster-img"
        loading="lazy"
      />
      <div v-else class="poster-placeholder">
        <el-icon :size="48"><Film /></el-icon>
      </div>
    </div>
    <div class="card-info">
      <h3 class="card-title">{{ movie.title }}</h3>
      <div class="card-meta">
        <span v-if="movie.year" class="year">{{ movie.year }}</span>
        <span v-if="movie.user_rating" class="rating">
          <span class="star-rating">{{ '★'.repeat(movie.user_rating) }}{{ '☆'.repeat(5 - movie.user_rating) }}</span>
        </span>
      </div>
      <div class="card-genres" v-if="genreList.length">
        <el-tag v-for="g in genreList.slice(0, 3)" :key="g" size="small" type="info" class="genre-tag">{{ g }}</el-tag>
      </div>
      <div class="card-date" v-if="movie.watch_date">{{ movie.watch_date }}</div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ movie: { type: Object, required: true } })

const posterUrl = computed(() => {
  if (!props.movie.poster_path) return null
  // 如果已经是完整URL（豆瓣），使用代理
  if (props.movie.poster_path.startsWith('http')) {
    return `/api/poster?url=${encodeURIComponent(props.movie.poster_path)}`
  }
  return props.movie.poster_path
})

const genreList = computed(() => {
  const text = props.movie.genres
  if (!text) return []
  try { return JSON.parse(text) } catch { /* not JSON */ }
  if (text.includes(' / ')) return text.split(' / ').map(s => s.trim()).filter(Boolean)
  return []
})
</script>

<style scoped>
.movie-card {
  width: 100%;
}
.movie-card :deep(.el-card__body) {
  padding: 0;
}
.card-poster {
  width: 100%;
  aspect-ratio: 2/3;
  background: #e4e7ed;
  overflow: hidden;
  border-radius: 4px 4px 0 0;
}
.poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}
.card-info {
  padding: 12px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #909399;
}
.card-genres {
  margin-bottom: 4px;
}
.card-date {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
