import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import InterviewPage from '../views/InterviewPage.vue'
import ReportPage from '../views/ReportPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/interview/:sessionId',
      name: 'interview',
      component: InterviewPage
    },
    {
      path: '/report/:sessionId',
      name: 'report',
      component: ReportPage
    }
  ]
})

export default router
