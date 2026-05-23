<script setup lang="ts">
import { ref } from 'vue'
import type { ChatMessage } from '../types'

const props = defineProps<{
  message: ChatMessage
}>()

const showThinking = ref(false)

function toggleThinking() {
  showThinking.value = !showThinking.value
}
</script>

<template>
  <div v-if="message.role === 'system'" class="flex justify-center mb-4">
    <div class="px-4 py-2 bg-amber-900/30 border border-amber-700/30 rounded-full">
      <p class="text-xs text-amber-400">{{ message.content }}</p>
    </div>
  </div>
  <div v-else :class="[
    'flex mb-4',
    message.role === 'candidate' ? 'justify-end' : 'justify-start'
  ]">
    <div :class="[
      'max-w-[75%] rounded-2xl px-4 py-3',
      message.role === 'candidate'
        ? 'bg-blue-600 text-white rounded-br-sm'
        : 'bg-gray-800 text-gray-100 rounded-bl-sm'
    ]">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-xs font-medium" :class="message.role === 'candidate' ? 'text-blue-200' : 'text-gray-400'">
          {{ message.role === 'candidate' ? '你' : '面试官' }}
        </span>
        <span v-if="message.stage" class="text-xs px-1.5 py-0.5 rounded bg-gray-700 text-gray-300">
          {{ message.stage === 'TECH' ? '技术面' : message.stage === 'PRESSURE' ? '压力面' : message.stage === 'COMPREHENSIVE' ? '综合面' : message.stage }}
        </span>
      </div>
      <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
      <div
        v-if="message.thinking && message.thinking.length > 0 && message.role === 'interviewer'"
        class="mt-2"
      >
        <button
          @click="toggleThinking"
          class="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          {{ showThinking ? '▼ 隐藏思考链' : '▶ 查看思考链' }}
        </button>
        <div v-if="showThinking" class="mt-1 p-2 bg-gray-900/50 rounded text-xs text-gray-500 space-y-1">
          <p v-for="(thought, i) in message.thinking" :key="i">💭 {{ thought }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
