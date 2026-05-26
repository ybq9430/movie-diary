import api from './index'

export const generatePersonality = () => api.post('/ai/personality')
export const getLatestPersonality = () => api.get('/ai/personality/latest')
export const generatePortrait = (style) => api.post('/ai/portrait', { style })
export const getLatestPortrait = () => api.get('/ai/portrait/latest')
export const getPortraitHistory = () => api.get('/ai/portrait/history')
export const generateRecommendations = () => api.post('/ai/recommend')
export const getRecommendations = () => api.get('/ai/recommendations')
export const markWatched = (id) => api.put(`/ai/recommendations/${id}/watched`)
