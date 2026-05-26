import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMovies, getMovie } from '../api/movie'

export const useMovieStore = defineStore('movie', () => {
  const movies = ref([])
  const currentMovie = ref(null)
  const total = ref(0)
  const page = ref(1)
  const perPage = ref(20)
  const pages = ref(0)
  const loading = ref(false)

  // Filters
  const filters = ref({
    search: '',
    genre: '',
    year_from: null,
    year_to: null,
    region: '',
    rating_min: null,
    rating_max: null,
    is_favorite: null,
    sort_by: 'watch_date',
    sort_order: 'desc',
  })

  async function fetchMovies() {
    loading.value = true
    try {
      const params = { page: page.value, per_page: perPage.value }
      for (const [k, v] of Object.entries(filters.value)) {
        if (v !== null && v !== '' && v !== undefined) params[k] = v
      }
      const data = await getMovies(params)
      movies.value = data.items
      total.value = data.total
      pages.value = data.pages
    } finally {
      loading.value = false
    }
  }

  async function fetchMovie(id) {
    loading.value = true
    try {
      currentMovie.value = await getMovie(id)
    } finally {
      loading.value = false
    }
  }

  return { movies, currentMovie, total, page, perPage, pages, loading, filters, fetchMovies, fetchMovie }
})
