<template>
  <div class="stats-view">
    <h1 class="page-title">统计分析</h1>

    <!-- Overview Cards -->
    <el-row :gutter="16" class="overview-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.total_movies || 0 }}</div>
          <div class="stat-label">总观影数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.avg_rating || '-' }}</div>
          <div class="stat-label">平均评分</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.favorite_genre || '-' }}</div>
          <div class="stat-label">最爱类型</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.time_span || '-' }}</div>
          <div class="stat-label">时间跨度</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>评分分布</template>
          <v-chart :option="ratingOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>类型偏好 Top 10</template>
          <v-chart :option="genreOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header>观影趋势</template>
          <v-chart :option="trendOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>最爱导演</template>
          <v-chart :option="directorOption" style="height: 400px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>地区分布</template>
          <v-chart :option="regionOption" style="height: 400px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>月份观影模式</template>
          <v-chart :option="monthOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>电影年代分布</template>
          <v-chart :option="yearOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import * as statsApi from '../api/stats'

use([CanvasRenderer, BarChart, PieChart, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const overview = ref({})
const ratingOption = ref({})
const genreOption = ref({})
const trendOption = ref({})
const directorOption = ref({})
const regionOption = ref({})
const monthOption = ref({})
const yearOption = ref({})

function barOption(data, color = '#409eff') {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: data.values, itemStyle: { color, borderRadius: [4, 4, 0, 0] } }],
  }
}

function horizontalBarOption(data, color = '#67c23a') {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: [...data.labels].reverse(), axisLabel: { width: 80, overflow: 'truncate' } },
    series: [{ type: 'bar', data: [...data.values].reverse(), itemStyle: { color, borderRadius: [0, 4, 4, 0] } }],
    grid: { left: 100 },
  }
}

function pieOption(data) {
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.labels.map((l, i) => ({ name: l, value: data.values[i] })),
      label: { show: true, formatter: '{b}: {c}' },
    }],
  }
}

function lineOption(data, color = '#e6a23c') {
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: data.values, smooth: true, areaStyle: { opacity: 0.1 }, itemStyle: { color } }],
    grid: { bottom: 60 },
  }
}

onMounted(async () => {
  const [
    ov, rating, genre, trend, director, region, month, year
  ] = await Promise.allSettled([
    statsApi.getOverview(),
    statsApi.getRatingDistribution(),
    statsApi.getGenrePreference(),
    statsApi.getWatchingTrend(),
    statsApi.getDirectorRanking(),
    statsApi.getRegionDistribution(),
    statsApi.getMonthlyPattern(),
    statsApi.getYearDistribution(),
  ])

  if (ov.status === 'fulfilled') overview.value = ov.value
  if (rating.status === 'fulfilled') ratingOption.value = barOption(rating.value, '#f7ba2a')
  if (genre.status === 'fulfilled') genreOption.value = pieOption(genre.value)
  if (trend.status === 'fulfilled') trendOption.value = lineOption(trend.value)
  if (director.status === 'fulfilled') directorOption.value = horizontalBarOption(director.value)
  if (region.status === 'fulfilled') regionOption.value = barOption(region.value, '#909399')
  if (month.status === 'fulfilled') monthOption.value = barOption(month.value, '#409eff')
  if (year.status === 'fulfilled') yearOption.value = barOption(year.value, '#67c23a')
})
</script>

<style scoped>
.stats-view {
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  margin-bottom: 20px;
}
.overview-row {
  margin-bottom: 20px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
.stat-label {
  text-align: center;
  color: #909399;
  margin-top: 4px;
}
</style>
