<template>
  <div class="import-view">
    <h1 class="page-title">数据导入</h1>

    <!-- CSV Import -->
    <el-card class="import-card" shadow="never">
      <template #header>
        <span>从 CSV 导入</span>
      </template>
      <p class="desc">导入已有的豆瓣观影数据 CSV 文件</p>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".csv"
            :limit="1"
          >
            <el-icon :size="48"><Upload /></el-icon>
            <div>拖拽文件到此处或<em>点击上传</em></div>
          </el-upload>
        </el-col>
        <el-col :span="12">
          <el-button type="primary" @click="importDefault" :loading="importing">
            导入默认 CSV
          </el-button>
          <el-button v-if="uploadFile" type="success" @click="importUpload" :loading="importing">
            导入上传的文件
          </el-button>
        </el-col>
      </el-row>

      <!-- Progress -->
      <div v-if="importStatus.status !== 'idle'" class="import-progress">
        <el-progress
          :percentage="importStatus.status === 'completed' ? 100 : undefined"
          :indeterminate="importStatus.status === 'running'"
          :status="importStatus.status === 'failed' ? 'exception' : importStatus.status === 'completed' ? 'success' : undefined"
        />
        <p class="progress-msg">{{ importStatus.message }}</p>
        <p v-if="importStatus.movie_count">已导入: {{ importStatus.movie_count }} 部</p>
      </div>
    </el-card>

    <!-- Douban Enrichment -->
    <el-card class="import-card" shadow="never">
      <template #header>
        <span>豆瓣数据补充</span>
      </template>
      <p class="desc">为缺少海报和简介的电影从豆瓣补充数据（需要网络访问豆瓣）</p>
      <el-button type="warning" @click="enrichAll" :loading="enriching">
        开始补充数据
      </el-button>

      <!-- Enrich Progress -->
      <div v-if="enrichStatus.status !== 'idle'" class="import-progress">
        <el-progress
          :percentage="enrichStatus.status === 'completed' ? 100 : undefined"
          :indeterminate="enrichStatus.status === 'running'"
          :status="enrichStatus.status === 'failed' ? 'exception' : enrichStatus.status === 'completed' ? 'success' : undefined"
        />
        <p class="progress-msg">{{ enrichStatus.message }}</p>
        <p v-if="enrichStatus.movie_count">已补充: {{ enrichStatus.movie_count }} 部</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { importCsv, importCsvUpload, getImportStatus, enrichAll as enrichAllApi, getEnrichStatus } from '../api/import'

const importing = ref(false)
const enriching = ref(false)
const uploadFile = ref(null)
const importStatus = ref({ status: 'idle', movie_count: 0, message: '' })
const enrichStatus = ref({ status: 'idle', movie_count: 0, message: '' })
let pollTimer = null
let enrichPollTimer = null

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const data = await getImportStatus()
      importStatus.value = data
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(pollTimer)
        importing.value = false
      }
    } catch {}
  }, 2000)
}

async function importDefault() {
  importing.value = true
  importStatus.value = { status: 'running', movie_count: 0, message: '开始导入...' }
  try {
    await importCsv()
    startPolling()
  } catch {
    importing.value = false
  }
}

async function importUpload() {
  if (!uploadFile.value) return
  importing.value = true
  importStatus.value = { status: 'running', movie_count: 0, message: '开始导入...' }
  try {
    await importCsvUpload(uploadFile.value.raw)
    startPolling()
  } catch {
    importing.value = false
  }
}

function handleFileChange(file) {
  uploadFile.value = file
}

function startEnrichPolling() {
  if (enrichPollTimer) clearInterval(enrichPollTimer)
  enrichPollTimer = setInterval(async () => {
    try {
      const data = await getEnrichStatus()
      enrichStatus.value = data
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(enrichPollTimer)
        enriching.value = false
      }
    } catch {}
  }, 3000)
}

async function enrichAll() {
  enriching.value = true
  enrichStatus.value = { status: 'running', movie_count: 0, message: '正在启动...' }
  try {
    const data = await enrichAllApi()
    if (data.status === 'running') {
      startEnrichPolling()
    } else {
      enrichStatus.value = { status: 'completed', movie_count: 0, message: data.message }
      enriching.value = false
    }
  } catch (e) {
    enrichStatus.value = { status: 'failed', movie_count: 0, message: '补充失败: ' + e.message }
    enriching.value = false
  }
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (enrichPollTimer) clearInterval(enrichPollTimer)
})
</script>

<style scoped>
.import-view {
  max-width: 800px;
  margin: 0 auto;
}
.import-card {
  margin-bottom: 20px;
}
.desc {
  color: #909399;
  margin-bottom: 16px;
}
.import-progress {
  margin-top: 20px;
}
.progress-msg {
  color: #606266;
  margin-top: 8px;
}
</style>
