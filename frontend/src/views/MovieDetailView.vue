<template>
  <div class="detail-view" v-loading="loading">
    <template v-if="movie">
      <!-- Backdrop -->
      <div class="backdrop" v-if="backdropUrl" :style="{ backgroundImage: `url(${backdropUrl})` }">
        <div class="backdrop-overlay"></div>
      </div>

      <el-card class="detail-card" shadow="never">
        <el-row :gutter="24">
          <!-- Poster -->
          <el-col :span="6">
            <div class="poster-wrap">
              <img v-if="posterUrl" :src="posterUrl" class="detail-poster" />
              <div v-else class="poster-placeholder-lg">
                <el-icon :size="64"><Film /></el-icon>
              </div>
            </div>
          </el-col>

          <!-- Info -->
          <el-col :span="18">
            <h1 class="movie-title">{{ movie.title }}</h1>
            <p class="movie-original" v-if="movie.original_title && movie.original_title !== movie.title">
              {{ movie.original_title }}
            </p>

            <div class="movie-meta">
              <el-tag v-if="movie.year">{{ movie.year }}</el-tag>
              <el-tag v-if="movie.runtime" type="info">{{ movie.runtime }}分钟</el-tag>
              <el-tag v-for="g in genreList" :key="g" type="warning" class="genre-tag">{{ g }}</el-tag>
            </div>

            <!-- User Rating -->
            <div class="user-section">
              <div class="rating-row">
                <span class="label">我的评分：</span>
                <el-rate v-model="editRating" :max="5" @change="saveRating" />
              </div>
              <div class="date-row">
                <span class="label">观影日期：</span>
                <el-date-picker v-model="editDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" @change="saveDate" />
              </div>
              <div class="fav-row">
                <span class="label">收藏：</span>
                <el-button :type="movie.is_favorite ? 'danger' : 'default'" :icon="Star" circle @click="toggleFav" />
              </div>
            </div>

            <!-- Directors & Cast -->
            <div class="info-section" v-if="directorList.length">
              <h3>导演</h3>
              <span>{{ directorList.join(' / ') }}</span>
            </div>
            <div class="info-section" v-if="castList.length">
              <h3>主演</h3>
              <span>{{ castList.slice(0, 8).join(' / ') }}</span>
            </div>

            <!-- Overview -->
            <div class="info-section" v-if="movie.overview">
              <h3>剧情简介</h3>
              <p class="overview-text">{{ movie.overview }}</p>
            </div>

            <!-- Comment & Impressions -->
            <div class="info-section">
              <h3>我的感想</h3>
              <el-input
                v-model="editImpressions"
                type="textarea"
                :rows="3"
                placeholder="写下你的感想..."
                @blur="saveImpressions"
              />
              <div v-if="movie.comment" class="comment-text">
                <el-tag type="info" size="small">豆瓣短评</el-tag>
                {{ movie.comment }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- Similar Movies -->
      <h2 class="section-title" style="margin-top: 24px;">相似电影</h2>
      <el-row :gutter="16">
        <el-col v-for="m in similarMovies" :key="m.id" :xs="12" :sm="8" :md="6" :lg="4">
          <el-card shadow="hover" class="similar-card" @click="$router.push(`/movies/${m.id}`)">
            <img v-if="m.poster_path" :src="getProxiedUrl(m.poster_path)" class="similar-poster" />
            <div class="similar-title">{{ m.title }}</div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Star } from '@element-plus/icons-vue'
import { getMovie, updateMovie } from '../api/movie'
import api from '../api/index'
import { ElMessage } from 'element-plus'

const route = useRoute()
const movie = ref(null)
const loading = ref(false)
const similarMovies = ref([])

const editRating = ref(0)
const editDate = ref('')
const editImpressions = ref('')

function getProxiedUrl(url) {
  if (!url) return null
  if (url.startsWith('http')) return `/api/poster?url=${encodeURIComponent(url)}`
  return url
}
const posterUrl = computed(() => getProxiedUrl(movie.value?.poster_path))
const backdropUrl = computed(() => getProxiedUrl(movie.value?.backdrop_path))

function parseJson(text) {
  if (!text) return []
  try { return JSON.parse(text) } catch { /* not JSON */ }
  if (text.includes(' / ')) return text.split(' / ').map(s => s.trim()).filter(Boolean)
  return []
}
const genreList = computed(() => parseJson(movie.value?.genres))
const directorList = computed(() => parseJson(movie.value?.directors))
const castList = computed(() => parseJson(movie.value?.cast_))

async function loadMovie(id) {
  loading.value = true
  try {
    const [movieData, similar] = await Promise.allSettled([
      getMovie(id),
      api.get(`/movies/${id}/similar`),
    ])
    if (movieData.status === 'fulfilled') {
      movie.value = movieData.value
      editRating.value = movie.value.user_rating || 0
      editDate.value = movie.value.watch_date || ''
      editImpressions.value = movie.value.impressions || ''
    }
    if (similar.status === 'fulfilled') {
      similarMovies.value = (similar.value || []).slice(0, 12)
    }
  } finally {
    loading.value = false
  }
}

async function saveRating(val) {
  const prev = movie.value.user_rating
  movie.value.user_rating = val
  try {
    await updateMovie(movie.value.id, { user_rating: val })
  } catch {
    movie.value.user_rating = prev
    ElMessage.error('保存评分失败')
  }
}

async function saveDate(val) {
  if (val) {
    try {
      await updateMovie(movie.value.id, { watch_date: val })
    } catch {
      ElMessage.error('保存日期失败')
    }
  }
}

async function saveImpressions() {
  try {
    await updateMovie(movie.value.id, { impressions: editImpressions.value })
  } catch {
    ElMessage.error('保存感想失败')
  }
}

async function toggleFav() {
  const newVal = !movie.value.is_favorite
  try {
    await updateMovie(movie.value.id, { is_favorite: newVal })
    movie.value.is_favorite = newVal
  } catch {
    ElMessage.error('操作失败')
  }
}

watch(() => route.params.id, (id) => { if (id) loadMovie(id) })
onMounted(() => loadMovie(route.params.id))
</script>

<style scoped>
.detail-view {
  max-width: 1100px;
  margin: 0 auto;
}
.backdrop {
  height: 300px;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  position: relative;
  margin-bottom: -100px;
}
.backdrop-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent, #f5f7fa);
  border-radius: 8px;
}
.detail-card {
  position: relative;
  z-index: 1;
}
.poster-wrap {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.detail-poster {
  width: 100%;
  display: block;
}
.poster-placeholder-lg {
  width: 100%;
  aspect-ratio: 2/3;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}
.movie-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}
.movie-original {
  color: #909399;
  margin-bottom: 12px;
}
.movie-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.user-section {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.user-section .label {
  display: inline-block;
  width: 80px;
  color: #606266;
}
.rating-row, .date-row, .fav-row {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}
.info-section {
  margin-bottom: 16px;
}
.info-section h3 {
  font-size: 15px;
  color: #303133;
  margin-bottom: 6px;
}
.overview-text {
  color: #606266;
  line-height: 1.8;
}
.comment-text {
  margin-top: 8px;
  color: #606266;
  font-style: italic;
}
.section-title {
  font-size: 20px;
  margin-bottom: 16px;
}
.similar-card {
  cursor: pointer;
}
.similar-poster {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  border-radius: 4px;
}
.similar-title {
  margin-top: 8px;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
