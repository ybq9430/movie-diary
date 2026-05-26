<template>
  <div class="portrait-view">
    <h1 class="page-title">AI 观影肖像</h1>
    <p class="page-desc">根据你的观影品味，AI 将为你创作一幅专属肖像</p>

    <!-- Style Selector -->
    <div class="style-selector">
      <el-radio-group v-model="selectedStyle" size="large">
        <el-radio-button value="水彩">水彩</el-radio-button>
        <el-radio-button value="油画">油画</el-radio-button>
        <el-radio-button value="波普艺术">波普艺术</el-radio-button>
        <el-radio-button value="极简主义">极简主义</el-radio-button>
        <el-radio-button value="赛博朋克">赛博朋克</el-radio-button>
        <el-radio-button value="水墨画">水墨画</el-radio-button>
      </el-radio-group>
    </div>

    <el-button
      type="primary"
      size="large"
      @click="generate"
      :loading="aiStore.loading"
      :icon="MagicStick"
      style="margin: 20px 0;"
    >
      生成肖像
    </el-button>

    <!-- Result -->
    <div v-if="aiStore.portrait" class="portrait-result">
      <el-card shadow="never" class="portrait-card">
        <div class="portrait-prompt">
          <h3>AI 生成的肖像描述</h3>
          <p>{{ aiStore.portrait.prompt }}</p>
          <el-tag>风格: {{ aiStore.portrait.style }}</el-tag>
        </div>
      </el-card>
    </div>

    <!-- History -->
    <div v-if="aiStore.portraitHistory.length" class="portrait-history">
      <h2>历史肖像</h2>
      <el-timeline>
        <el-timeline-item
          v-for="p in aiStore.portraitHistory"
          :key="p.id"
          :timestamp="p.created_at"
          placement="top"
        >
          <el-card shadow="hover">
            <el-tag size="small" style="margin-bottom: 8px;">{{ p.style }}</el-tag>
            <p style="color: #606266; font-size: 14px;">{{ p.prompt }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import { useAiStore } from '../stores/ai'

const aiStore = useAiStore()
const selectedStyle = ref('水彩')

async function generate() {
  await aiStore.createPortrait(selectedStyle.value)
}

onMounted(() => {
  aiStore.fetchPortrait()
  aiStore.fetchPortraitHistory()
})
</script>

<style scoped>
.portrait-view {
  max-width: 800px;
  margin: 0 auto;
}
.page-desc {
  color: #909399;
  margin-bottom: 20px;
}
.style-selector {
  margin-bottom: 12px;
}
.portrait-result {
  margin-top: 20px;
}
.portrait-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 16px;
  color: #fff;
}
.portrait-card :deep(.el-card__body) {
  padding: 32px;
}
.portrait-prompt h3 {
  margin-bottom: 12px;
}
.portrait-prompt p {
  line-height: 1.8;
  margin-bottom: 12px;
}
.portrait-history {
  margin-top: 32px;
}
.portrait-history h2 {
  margin-bottom: 16px;
}
</style>
