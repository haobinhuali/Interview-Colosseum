<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../store/interview'
import ChatBubble from '../components/ChatBubble.vue'
import StageIndicator from '../components/StageIndicator.vue'
import type { StageType } from '../types'

const store = useInterviewStore()
const route = useRoute()
const router = useRouter()

const userInput = ref('')
const chatContainer = ref<HTMLDivElement>()
const showStageTransition = ref(false)
const transitionMessage = ref('')
const showConfirmDialog = ref(false)
const confirmAction = ref<'skip' | 'jump' | null>(null)

const stageTransitionMessages: Record<string, string> = {
  TECH: '🔵 进入技术深潜面 — 准备好展示你的技术深度',
  PRESSURE: '🔴 进入压力挑战面 — 面试官将针对你的薄弱点发起挑战',
  COMPREHENSIVE: '🟢 进入综合面 — 放松一下，聊聊整体感受'
}

const stageBackgrounds: Record<string, string> = {
  TECH: 'bg-gray-900',
  PRESSURE: 'bg-red-950/30',
  COMPREHENSIVE: 'bg-gray-900'
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const answer = userInput.value.trim()
  if (!answer || store.loading) return

  userInput.value = ''
  const previousStage = store.stage

  try {
    await store.sendAnswer(answer)
    scrollToBottom()

    if (store.stage !== previousStage && store.stage !== 'DONE') {
      showStageTransition.value = true
      transitionMessage.value = stageTransitionMessages[store.stage] || '切换阶段中...'
      setTimeout(() => {
        showStageTransition.value = false
      }, 2500)
    }

    if (store.finished) {
      try {
        await store.fetchReport()
        router.push(`/report/${store.sessionId}`)
      } catch {
        // report generation error handled in store
      }
    }
  } catch {
    // error handled in store
  }
}

function requestSkipStage() {
  confirmAction.value = 'skip'
  showConfirmDialog.value = true
}

function requestJumpToFinal() {
  confirmAction.value = 'jump'
  showConfirmDialog.value = true
}

function cancelConfirm() {
  showConfirmDialog.value = false
  confirmAction.value = null
}

async function executeConfirmAction() {
  showConfirmDialog.value = false
  const action = confirmAction.value
  confirmAction.value = null

  const previousStage = store.stage

  try {
    if (action === 'skip') {
      await store.skipCurrentStage()
    } else if (action === 'jump') {
      await store.jumpToFinalEvaluation()
    }

    scrollToBottom()

    if (store.stage !== previousStage && store.stage !== 'DONE') {
      showStageTransition.value = true
      transitionMessage.value = stageTransitionMessages[store.stage] || '切换阶段中...'
      setTimeout(() => {
        showStageTransition.value = false
      }, 2500)
    }

    if (store.finished) {
      try {
        await store.fetchReport()
        router.push(`/report/${store.sessionId}`)
      } catch {
        // report generation error handled in store
      }
    }
  } catch {
    // error handled in store
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

watch(() => store.conversations.length, () => {
  scrollToBottom()
})

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div :class="['flex flex-col h-[calc(100vh-120px)] transition-colors duration-700', stageBackgrounds[store.stage] || 'bg-gray-900']">
    <StageIndicator
      :current-stage="store.stage as StageType"
      :round="store.round"
      :max-rounds="8"
    />

    <div
      v-if="showStageTransition"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div class="text-center animate-pulse">
        <p class="text-2xl font-bold text-white">{{ transitionMessage }}</p>
      </div>
    </div>

    <div
      v-if="showConfirmDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div class="bg-gray-800 rounded-2xl p-6 max-w-md mx-4 border border-gray-700">
        <h3 class="text-lg font-semibold text-white mb-3">
          {{ confirmAction === 'skip' ? '确认跳过本轮面试？' : '确认直接进入最终评估？' }}
        </h3>
        <p class="text-gray-400 text-sm mb-5">
          {{ confirmAction === 'skip'
            ? '跳过后将根据已有对话对当前阶段进行评估，然后进入下一阶段面试。'
            : '将跳过所有剩余面试阶段，根据已有对话直接生成最终评估报告。'
          }}
        </p>
        <div class="flex gap-3 justify-end">
          <button
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors text-sm"
            @click="cancelConfirm"
          >
            取消
          </button>
          <button
            class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors text-sm font-medium"
            @click="executeConfirmAction"
          >
            确认
          </button>
        </div>
      </div>
    </div>

    <div
      ref="chatContainer"
      class="flex-1 overflow-y-auto px-4 py-2"
    >
      <ChatBubble
        v-for="(msg, i) in store.conversations"
        :key="i"
        :message="msg"
      />
      <div v-if="store.loading" class="flex justify-start mb-4">
        <div class="bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-3">
          <div class="flex items-center gap-2 text-gray-400 text-sm">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0ms" />
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 150ms" />
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="store.error" class="px-4 py-2">
      <div class="p-2 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-sm">
        {{ store.error }}
      </div>
    </div>

    <div class="border-t border-gray-800 p-4">
      <div class="flex gap-2 mb-2" v-if="!store.finished && store.stage !== 'DONE' && store.stage !== 'INIT'">
        <button
          :disabled="store.loading"
          class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-400 hover:text-gray-300 text-xs rounded-lg border border-gray-700 transition-colors"
          @click="requestSkipStage"
        >
          ⏭ 跳过本轮面试
        </button>
        <button
          :disabled="store.loading"
          class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-400 hover:text-gray-300 text-xs rounded-lg border border-gray-700 transition-colors"
          @click="requestJumpToFinal"
        >
          ⏩ 直接到最终评估
        </button>
      </div>
      <div class="flex gap-3">
        <textarea
          v-model="userInput"
          :disabled="store.loading || store.finished"
          placeholder="输入你的回答... (Enter 发送, Shift+Enter 换行)"
          rows="1"
          class="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:opacity-50"
          @keydown="handleKeydown"
        />
        <button
          :disabled="store.loading || store.finished || !userInput.trim()"
          class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium rounded-xl transition-colors"
          @click="sendMessage"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>
