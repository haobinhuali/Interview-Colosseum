<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../store/interview'

const store = useInterviewStore()
const router = useRouter()

const isDragging = ref(false)
const jobType = ref('AI Agent 开发工程师')
const file = ref<File | null>(null)
const uploadSuccess = ref(false)
const errorMessage = ref('')

const jobOptions = [
  'AI Agent 开发工程师',
  '前端开发工程师',
  '后端开发工程师',
  '全栈开发工程师',
  '算法工程师',
  '数据工程师'
]

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const droppedFile = e.dataTransfer?.files[0]
  if (droppedFile && droppedFile.type === 'application/pdf') {
    file.value = droppedFile
    handleUpload()
  } else {
    errorMessage.value = '请上传 PDF 格式的简历'
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
    handleUpload()
  }
}

async function handleUpload() {
  if (!file.value) return
  errorMessage.value = ''
  try {
    await store.uploadResume(file.value)
    uploadSuccess.value = true
  } catch {
    errorMessage.value = store.error || '上传失败'
  }
}

async function handleStartInterview() {
  errorMessage.value = ''
  try {
    await store.startInterview(jobType.value)
    router.push(`/interview/${store.sessionId}`)
  } catch {
    errorMessage.value = store.error || '启动面试失败'
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="text-center mb-10">
      <h2 class="text-4xl font-bold mb-3">
        ⚔️ 面试角斗场
      </h2>
      <p class="text-gray-400 text-lg">
        三位 AI 面试官，递进式挑战，全方位评估
      </p>
    </div>

    <div
      :class="[
        'border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer mb-6',
        isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-gray-700 hover:border-gray-500',
        uploadSuccess ? 'border-green-500 bg-green-500/5' : ''
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="($refs.fileInput as HTMLInputElement)?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        class="hidden"
        @change="handleFileSelect"
      />
      <div v-if="!uploadSuccess">
        <div class="text-4xl mb-3">📄</div>
        <p class="text-gray-300 mb-1">拖拽 PDF 简历到此处，或点击上传</p>
        <p class="text-gray-500 text-sm">仅支持 PDF 格式</p>
      </div>
      <div v-else class="text-green-400">
        <div class="text-4xl mb-3">✅</div>
        <p class="mb-1">简历上传成功</p>
        <p class="text-sm text-gray-400">{{ file?.name }}</p>
      </div>
    </div>

    <div v-if="errorMessage" class="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
      {{ errorMessage }}
    </div>

    <div v-if="store.loading" class="text-center py-4">
      <div class="inline-block w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      <span class="ml-2 text-gray-400">处理中...</span>
    </div>

    <div v-if="uploadSuccess && store.parsedResume" class="mb-6">
      <h3 class="text-lg font-semibold mb-3 text-gray-200">📋 简历解析结果</h3>
      <div class="bg-gray-800 rounded-xl p-5 space-y-4">
        <div>
          <span class="text-gray-400 text-sm">姓名：</span>
          <span class="text-white font-medium">{{ store.parsedResume.name }}</span>
        </div>
        <div>
          <span class="text-gray-400 text-sm">技能：</span>
          <div class="flex flex-wrap gap-2 mt-1">
            <span
              v-for="skill in store.parsedResume.skills"
              :key="skill"
              class="px-2.5 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full"
            >
              {{ skill }}
            </span>
          </div>
        </div>
        <div v-if="store.parsedResume.projects.length > 0">
          <span class="text-gray-400 text-sm">项目经历：</span>
          <div class="space-y-2 mt-2">
            <div
              v-for="project in store.parsedResume.projects"
              :key="project.name"
              class="bg-gray-900/50 rounded-lg p-3"
            >
              <p class="text-white font-medium text-sm">{{ project.name }}</p>
              <p class="text-gray-400 text-xs mt-1">{{ project.description }}</p>
              <div class="flex flex-wrap gap-1.5 mt-2">
                <span
                  v-for="tech in project.tech_stack"
                  :key="tech"
                  class="px-2 py-0.5 bg-green-500/15 text-green-300 text-xs rounded"
                >
                  {{ tech }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="uploadSuccess" class="mb-6">
      <label class="block text-sm text-gray-400 mb-2">选择岗位类型</label>
      <select
        v-model="jobType"
        class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option v-for="option in jobOptions" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <button
      v-if="uploadSuccess"
      :disabled="store.loading"
      class="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-xl transition-colors duration-200"
      @click="handleStartInterview"
    >
      🏟️ 开始面试
    </button>
  </div>
</template>
