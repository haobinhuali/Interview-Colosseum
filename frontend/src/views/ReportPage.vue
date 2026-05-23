<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../store/interview'
import RadarChart from '../components/RadarChart.vue'

const store = useInterviewStore()
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  if (!store.report && store.sessionId) {
    try {
      await store.fetchReport()
    } catch {
      // handled in store
    }
  }
})

function getScoreColor(score: number): string {
  if (score >= 8) return 'text-green-400'
  if (score >= 6) return 'text-blue-400'
  if (score >= 4) return 'text-yellow-400'
  return 'text-red-400'
}

function getScoreRingColor(score: number): string {
  if (score >= 8) return '#22c55e'
  if (score >= 6) return '#3b82f6'
  if (score >= 4) return '#eab308'
  return '#ef4444'
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="store.loading" class="text-center py-20">
      <div class="inline-block w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <p class="mt-4 text-gray-400">正在生成评估报告...</p>
    </div>

    <div v-else-if="store.error" class="text-center py-20">
      <p class="text-red-400 mb-4">{{ store.error }}</p>
      <button
        class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        @click="store.fetchReport()"
      >
        重试
      </button>
    </div>

    <div v-else-if="store.report" class="space-y-8">
      <div class="text-center">
        <h2 class="text-3xl font-bold mb-2">🏟️ 面试评估报告</h2>
        <p class="text-gray-400">Interview Colosseum 评估结果</p>
      </div>

      <div class="flex items-center justify-center">
        <div class="relative w-40 h-40">
          <svg class="w-40 h-40 transform -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#1f2937" stroke-width="8" />
            <circle
              cx="60" cy="60" r="54" fill="none"
              :stroke="getScoreRingColor(store.report.weighted_total)"
              stroke-width="8"
              stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 54"
              :stroke-dashoffset="2 * Math.PI * 54 * (1 - store.report.weighted_total / 10)"
              class="transition-all duration-1000"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span :class="['text-3xl font-bold', getScoreColor(store.report.weighted_total)]">
              {{ store.report.weighted_total }}
            </span>
            <span class="text-gray-400 text-xs">/10</span>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold mb-3 text-gray-200">📝 综合评价</h3>
        <p class="text-gray-300 leading-relaxed">{{ store.report.summary }}</p>
      </div>

      <div class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-200">📊 能力雷达图</h3>
        <RadarChart :data="store.report.radar_data" />
      </div>

      <div class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-200">🎯 分项评分</h3>
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="item in store.report.radar_data"
            :key="item.dim"
            class="bg-gray-900/50 rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-gray-400 text-sm">{{ item.dim }}</span>
              <span :class="['text-lg font-bold', getScoreColor(item.score)]">{{ item.score }}</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-700"
                :style="{
                  width: (item.score / 10 * 100) + '%',
                  backgroundColor: getScoreRingColor(item.score)
                }"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6">
        <h3 class="text-lg font-semibold mb-4 text-gray-200">💡 改进建议</h3>
        <div class="space-y-4">
          <div
            v-for="(suggestion, i) in store.report.suggestions"
            :key="i"
            class="bg-gray-900/50 rounded-lg p-4 border-l-4 border-blue-500"
          >
            <h4 class="text-white font-medium mb-2">{{ suggestion.title }}</h4>
            <p class="text-gray-300 text-sm leading-relaxed mb-2">{{ suggestion.content }}</p>
            <div v-if="suggestion.evidence" class="mt-2 p-2 bg-gray-800 rounded text-xs text-yellow-400/80 italic">
              💬 "{{ suggestion.evidence }}"
            </div>
          </div>
        </div>
      </div>

      <div class="text-center pb-8">
        <button
          class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors"
          @click="store.reset(); router.push('/')"
        >
          🔄 开始新的面试
        </button>
      </div>
    </div>
  </div>
</template>
