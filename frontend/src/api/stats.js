import api from './index'

export const getOverview = () => api.get('/stats/overview')
export const getRatingDistribution = () => api.get('/stats/rating-distribution')
export const getGenrePreference = () => api.get('/stats/genre-preference')
export const getWatchingTrend = () => api.get('/stats/watching-trend')
export const getDirectorRanking = () => api.get('/stats/director-ranking')
export const getRegionDistribution = () => api.get('/stats/region-distribution')
export const getMonthlyPattern = () => api.get('/stats/monthly-pattern')
export const getYearDistribution = () => api.get('/stats/year-distribution')
