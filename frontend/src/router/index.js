import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
  { path: '/movies', name: 'Movies', component: () => import('../views/MovieCatalogView.vue') },
  { path: '/movies/:id', name: 'MovieDetail', component: () => import('../views/MovieDetailView.vue') },
  { path: '/stats', name: 'Stats', component: () => import('../views/StatsView.vue') },
  { path: '/import', name: 'Import', component: () => import('../views/ImportView.vue') },
  { path: '/scrape', name: 'Scrape', component: () => import('../views/ScrapeView.vue') },
  { path: '/personality', name: 'Personality', component: () => import('../views/PersonalityView.vue') },
  { path: '/portrait', name: 'Portrait', component: () => import('../views/PortraitView.vue') },
  { path: '/recommend', name: 'Recommend', component: () => import('../views/RecommendView.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})
