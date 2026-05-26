<template>
  <div class="scrape-view">
    <h1 class="page-title">豆瓣观影抓取</h1>
    <p class="page-desc">输入豆瓣用户 ID，抓取该用户标记为「看过」的电影</p>

    <!-- Input Section -->
    <el-card class="input-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="7">
          <el-input
            v-model="userId"
            placeholder="豆瓣用户 ID（如 183593062）"
            clearable
            :disabled="scraping"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="cookie"
            placeholder="Cookie（可选，私密主页需要）"
            clearable
            :disabled="scraping"
          />
        </el-col>
        <el-col :span="4">
          <el-checkbox v-model="fetchDetail" :disabled="scraping">
            抓取详情页
          </el-checkbox>
        </el-col>
        <el-col :span="4">
          <el-button
            type="primary"
            :loading="scraping"
            :disabled="!userId.trim()"
            @click="startScrape"
          >
            开始抓取
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button
            v-if="status.status === 'completed'"
            type="success"
            @click="downloadCsv"
          >
            下载 CSV
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Progress -->
    <el-card v-if="status.status !== 'idle'" class="progress-card" shadow="never">
      <el-progress
        :percentage="status.status === 'completed' ? 100 : undefined"
        :indeterminate="status.status === 'running'"
        :status="status.status === 'failed' ? 'exception' : status.status === 'completed' ? 'success' : undefined"
      />
      <p class="progress-msg">{{ status.message }}</p>
      <p v-if="status.movie_count" class="progress-count">
        已抓取: {{ status.movie_count }} 部电影
      </p>
    </el-card>

    <!-- Results Table -->
    <el-card v-if="results.length" class="results-card" shadow="never">
      <template #header>
        <div class="results-header">
          <span>抓取结果（共 {{ total }} 部）</span>
        </div>
      </template>

      <el-table :data="results" stripe style="width: 100%" max-height="600">
        <el-table-column prop="title" label="片名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="year" label="年份" width="80" align="center" />
        <el-table-column prop="director" label="导演" min-width="150" show-overflow-tooltip />
        <el-table-column prop="genre" label="类型" min-width="150" show-overflow-tooltip />
        <el-table-column prop="region" label="地区" width="100" show-overflow-tooltip />
        <el-table-column prop="user_rating" label="评分" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.user_rating" class="star-rating">
              {{ '★'.repeat(row.user_rating) }}{{ '☆'.repeat(5 - row.user_rating) }}
            </span>
            <span v-else class="no-rating">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="watch_date" label="观影日期" width="120" align="center" />
        <el-table-column prop="duration" label="片长" width="90" align="center" />
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="fetchResults"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api/index'

const userId = ref('')
const cookie = ref('')
const fetchDetail = ref(false)
const scraping = ref(false)
const status = ref({ status: 'idle', movie_count: 0, message: '' })
const results = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(20)

let pollTimer = null

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const data = await api.get('/scrape/status')
      status.value = data
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(pollTimer)
        scraping.value = false
        if (data.status === 'completed') {
          fetchResults()
        }
      }
    } catch {
      // ignore poll errors
    }
  }, 2000)
}

async function startScrape() {
  if (!userId.value.trim()) return
  scraping.value = true
  results.value = []
  total.value = 0
  currentPage.value = 1
  status.value = { status: 'running', movie_count: 0, message: '正在启动抓取...' }

  try {
    await api.post('/scrape', {
      user_id: userId.value.trim(),
      cookie: cookie.value.trim(),
      detail: fetchDetail.value,
    })
    startPolling()
  } catch (e) {
    scraping.value = false
    status.value = { status: 'failed', movie_count: 0, message: e.response?.data?.detail || '启动失败' }
  }
}

async function fetchResults() {
  try {
    const data = await api.get('/scrape/results', {
      params: { page: currentPage.value, per_page: perPage.value },
    })
    results.value = data.items || []
    total.value = data.total || 0
  } catch {
    ElMessage.error('获取结果失败')
  }
}

function downloadCsv() {
  window.open('/api/scrape/download', '_blank')
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.scrape-view {
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}
.page-desc {
  color: #909399;
  margin-bottom: 20px;
}
.input-card {
  margin-bottom: 16px;
}
.progress-card {
  margin-bottom: 16px;
}
.progress-msg {
  color: #606266;
  margin-top: 12px;
  font-size: 14px;
}
.progress-count {
  color: #409eff;
  font-weight: bold;
  margin-top: 4px;
}
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
.star-rating {
  color: #f7ba2a;
  font-size: 13px;
}
.no-rating {
  color: #c0c4cc;
}
</style>
