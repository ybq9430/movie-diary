<template>
  <div class="recommend-view">
    <h1 class="page-title">AI 智能推荐</h1>
    <p class="page-desc">基于你的观影偏好，AI 为你推荐你可能喜欢的电影</p>

    <el-button
      type="primary"
      size="large"
      @click="generate"
      :loading="aiStore.loading"
      :icon="MagicStick"
    >
      {{ aiStore.recommendations.length ? '重新推荐' : '获取推荐' }}
    </el-button>

    <!-- Recommendations -->
    <div v-if="aiStore.recommendations.length" class="rec-list">
      <el-row :gutter="16">
        <el-col v-for="rec in aiStore.recommendations" :key="rec.id" :span="8">
          <el-card shadow="hover" class="rec-card">
            <div class="rec-poster">
              <img
                v-if="rec.poster_path"
                :src="rec.poster_path.startsWith('http') ? `/api/poster?url=${encodeURIComponent(rec.poster_path)}` : rec.poster_path"
                class="poster-img"
              />
              <div v-else class="poster-placeholder">
                <el-icon :size="48"><Film /></el-icon>
              </div>
            </div>
            <h3 class="rec-title">{{ rec.movie_title }}</h3>
            <p class="rec-reason">{{ rec.reason }}</p>
            <el-button
              size="small"
              type="success"
              @click="markWatched(rec)"
              :disabled="rec.is_watched"
            >
              {{ rec.is_watched ? '已看过' : '标记已看' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-empty v-else-if="!aiStore.loading" description="点击上方按钮获取 AI 推荐" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import { useAiStore } from '../stores/ai'
import { markWatched as markWatchedApi } from '../api/ai'
import { ElMessage } from 'element-plus'

const aiStore = useAiStore()

async function generate() {
  await aiStore.createRecommendations()
}

async function markWatched(rec) {
  try {
    await markWatchedApi(rec.id)
    rec.is_watched = true
    ElMessage.success('已标记为看过')
  } catch {
    ElMessage.error('标记失败，请重试')
  }
}

onMounted(() => aiStore.fetchRecommendations())
</script>

<style scoped>
.recommend-view {
  max-width: 1200px;
  margin: 0 auto;
}
.page-desc {
  color: #909399;
  margin-bottom: 20px;
}
.rec-list {
  margin-top: 24px;
}
.rec-card {
  margin-bottom: 16px;
}
.rec-poster {
  width: 100%;
  aspect-ratio: 2/3;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}
.poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}
.rec-title {
  font-size: 16px;
  margin-bottom: 8px;
}
.rec-reason {
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
}
</style>
