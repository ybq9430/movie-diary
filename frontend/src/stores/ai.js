import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  generatePersonality, getLatestPersonality,
  generatePortrait, getLatestPortrait, getPortraitHistory,
  generateRecommendations, getRecommendations,
} from '../api/ai'

export const useAiStore = defineStore('ai', () => {
  const personality = ref(null)
  const portrait = ref(null)
  const portraitHistory = ref([])
  const recommendations = ref([])
  const loading = ref(false)

  async function fetchPersonality() {
    try {
      personality.value = await getLatestPersonality()
    } catch { /* handled by axios interceptor */ }
  }

  async function createPersonality() {
    loading.value = true
    try {
      personality.value = await generatePersonality()
    } finally {
      loading.value = false
    }
  }

  async function fetchPortrait() {
    try {
      portrait.value = await getLatestPortrait()
    } catch { /* handled by axios interceptor */ }
  }

  async function createPortrait(style) {
    loading.value = true
    try {
      portrait.value = await generatePortrait(style)
    } finally {
      loading.value = false
    }
  }

  async function fetchPortraitHistory() {
    try {
      portraitHistory.value = await getPortraitHistory()
    } catch { /* handled by axios interceptor */ }
  }

  async function fetchRecommendations() {
    try {
      recommendations.value = await getRecommendations()
    } catch { /* handled by axios interceptor */ }
  }

  async function createRecommendations() {
    loading.value = true
    try {
      recommendations.value = await generateRecommendations()
    } finally {
      loading.value = false
    }
  }

  return {
    personality, portrait, portraitHistory, recommendations, loading,
    fetchPersonality, createPersonality,
    fetchPortrait, createPortrait, fetchPortraitHistory,
    fetchRecommendations, createRecommendations,
  }
})
