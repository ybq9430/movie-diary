<template>
  <div class="catalog-view">
    <!-- Search & Filter Bar -->
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input
            v-model="store.filters.search"
            placeholder="搜索电影名称..."
            clearable
            @keyup.enter="store.fetchMovies()"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="store.filters.sort_by" placeholder="排序" @change="store.fetchMovies()">
            <el-option label="观影日期" value="watch_date" />
            <el-option label="评分" value="user_rating" />
            <el-option label="年份" value="year" />
            <el-option label="片名" value="title" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="store.filters.sort_order" @change="store.fetchMovies()">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-input v-model="store.filters.genre" placeholder="类型筛选" clearable @change="store.fetchMovies()" />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="store.fetchMovies()">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="16" align="middle" style="margin-top: 12px;">
        <el-col :span="4">
          <el-input v-model="store.filters.region" placeholder="地区筛选" clearable @change="store.fetchMovies()" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="store.filters.is_favorite" placeholder="收藏状态" clearable @change="store.fetchMovies()">
            <el-option label="已收藏" :value="true" />
            <el-option label="未收藏" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="store.filters.rating_min" placeholder="最低评分" clearable @change="store.fetchMovies()">
            <el-option label="不限" :value="null" />
            <el-option v-for="n in 5" :key="n" :label="`${n}星及以上`" :value="n" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="resetFilters">重置筛选</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Movie Grid -->
    <div v-loading="store.loading" class="movie-grid">
      <MovieCard v-for="movie in store.movies" :key="movie.id" :movie="movie" />
    </div>

    <!-- Pagination -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="store.page"
        :page-size="store.perPage"
        :total="store.total"
        layout="prev, pager, next, total"
        @current-change="store.fetchMovies()"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useMovieStore } from '../stores/movie'
import MovieCard from '../components/movie/MovieCard.vue'

const store = useMovieStore()

function resetFilters() {
  store.filters.search = ''
  store.filters.genre = ''
  store.filters.region = ''
  store.filters.is_favorite = null
  store.filters.rating_min = null
  store.filters.year_from = null
  store.filters.year_to = null
  store.filters.sort_by = 'watch_date'
  store.filters.sort_order = 'desc'
  store.fetchMovies()
}

onMounted(() => store.fetchMovies())
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}
.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.pagination-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
