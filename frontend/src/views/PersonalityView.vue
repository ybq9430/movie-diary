<template>
  <div class="personality-view">
    <h1 class="page-title">AI 观影性格分析</h1>
    <p class="page-desc">基于你的观影历史，AI 将为你生成一份专属的观影性格报告</p>

    <el-button
      type="primary"
      size="large"
      @click="generate"
      :loading="aiStore.loading"
      :icon="MagicStick"
    >
      {{ aiStore.personality ? '重新生成' : '生成性格分析' }}
    </el-button>

    <!-- Result -->
    <div v-if="aiStore.personality">
      <div class="export-actions">
        <el-button @click="saveAsImage" :icon="Download">保存为图片</el-button>
        <el-button @click="saveAsPdf" :icon="Document">保存为 PDF</el-button>
      </div>
      <div ref="resultCardRef" class="result-card">
        <div class="result-meta">
          <el-tag>分析了 {{ aiStore.personality.movie_count }} 部电影</el-tag>
          <span class="result-date">{{ aiStore.personality.created_at }}</span>
        </div>
        <div class="result-content" v-html="renderedAnalysis"></div>
      </div>
    </div>

    <!-- Empty State -->
    <el-empty v-else-if="!aiStore.loading" description="点击上方按钮生成你的观影性格分析" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { MagicStick, Download, Document } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAiStore } from '../stores/ai'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const aiStore = useAiStore()
const resultCardRef = ref(null)

const renderedAnalysis = computed(() => {
  if (!aiStore.personality?.analysis) return ''
  return DOMPurify.sanitize(marked(aiStore.personality.analysis))
})

async function generate() {
  await aiStore.createPersonality()
}

function getFilename(suffix) {
  const date = new Date().toISOString().slice(0, 10)
  return `观影性格分析_${date}.${suffix}`
}

async function captureCard() {
  return await html2canvas(resultCardRef.value, {
    scale: 2,
    backgroundColor: null,
    useCORS: true
  })
}

async function saveAsImage() {
  const canvas = await captureCard()
  const link = document.createElement('a')
  link.download = getFilename('png')
  link.href = canvas.toDataURL('image/png')
  link.click()
}

async function saveAsPdf() {
  const canvas = await captureCard()
  const imgData = canvas.toDataURL('image/png')
  const imgWidth = canvas.width
  const imgHeight = canvas.height

  const pdf = new jsPDF({
    orientation: imgWidth > imgHeight ? 'landscape' : 'portrait',
    unit: 'px',
    format: [imgWidth, imgHeight]
  })

  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)
  pdf.save(getFilename('pdf'))
}

onMounted(() => aiStore.fetchPersonality())
</script>

<style scoped>
.personality-view {
  max-width: 800px;
  margin: 0 auto;
}
.page-desc {
  color: #909399;
  margin-bottom: 20px;
}
.export-actions {
  margin-top: 24px;
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  color: #fff;
}
.result-meta {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.result-date {
  opacity: 0.7;
  font-size: 14px;
}
.result-content {
  line-height: 1.8;
}
.result-content :deep(h1),
.result-content :deep(h2),
.result-content :deep(h3) {
  color: #fff;
  margin-top: 20px;
  margin-bottom: 8px;
}
.result-content :deep(p) {
  margin-bottom: 12px;
}
.result-content :deep(ul),
.result-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}
</style>
