import { defineStore } from 'pinia'
import { ref } from 'vue'
import { uploadResume as apiUploadResume, startInterview as apiStartInterview, interviewNext as apiInterviewNext, generateReport as apiGenerateReport, skipStage as apiSkipStage, jumpToFinal as apiJumpToFinal } from '../api'
import type { ParsedResume, ChatMessage, Report, StageType } from '../types'

export const useInterviewStore = defineStore('interview', () => {
  const resumeId = ref('')
  const parsedResume = ref<ParsedResume | null>(null)
  const sessionId = ref('')
  const stage = ref<StageType>('INIT')
  const round = ref(0)
  const finished = ref(false)
  const conversations = ref<ChatMessage[]>([])
  const report = ref<Report | null>(null)
  const loading = ref(false)
  const error = ref('')

  async function uploadResume(file: File) {
    loading.value = true
    error.value = ''
    try {
      const result = await apiUploadResume(file)
      resumeId.value = result.resume_id
      parsedResume.value = result.parsed_data
    } catch (e: any) {
      error.value = e.response?.data?.detail || '简历上传失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function startInterview(jobType: string) {
    loading.value = true
    error.value = ''
    try {
      const result = await apiStartInterview(resumeId.value, jobType)
      sessionId.value = result.session_id
      stage.value = result.stage as StageType
      conversations.value = [{
        role: 'interviewer',
        content: result.first_message,
        stage: result.stage,
        thinking: result.thinking
      }]
      round.value = 1
    } catch (e: any) {
      error.value = e.response?.data?.detail || '启动面试失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function sendAnswer(answer: string) {
    loading.value = true
    error.value = ''
    conversations.value.push({
      role: 'candidate',
      content: answer,
      stage: stage.value
    })
    try {
      const result = await apiInterviewNext(sessionId.value, answer)
      conversations.value.push({
        role: 'interviewer',
        content: result.message,
        stage: result.stage,
        thinking: result.thinking
      })
      stage.value = result.stage as StageType
      round.value = result.round
      finished.value = result.finished
    } catch (e: any) {
      error.value = e.response?.data?.detail || '发送回答失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function skipCurrentStage() {
    loading.value = true
    error.value = ''
    try {
      const result = await apiSkipStage(sessionId.value)
      conversations.value.push({
        role: 'system',
        content: '⏭ 已跳过当前面试阶段',
        stage: stage.value
      })
      if (result.finished) {
        stage.value = 'DONE'
        finished.value = true
      } else {
        conversations.value.push({
          role: 'interviewer',
          content: result.message,
          stage: result.stage,
          thinking: result.thinking
        })
        stage.value = result.stage as StageType
        round.value = result.round
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || '跳过阶段失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function jumpToFinalEvaluation() {
    loading.value = true
    error.value = ''
    try {
      const result = await apiJumpToFinal(sessionId.value)
      conversations.value.push({
        role: 'system',
        content: '⏩ 已跳过所有剩余阶段，直接进入最终评估',
        stage: stage.value
      })
      stage.value = 'DONE'
      finished.value = true
    } catch (e: any) {
      error.value = e.response?.data?.detail || '跳转到最终评估失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchReport() {
    loading.value = true
    error.value = ''
    try {
      const result = await apiGenerateReport(sessionId.value)
      report.value = result.report
    } catch (e: any) {
      error.value = e.response?.data?.detail || '生成报告失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  function reset() {
    resumeId.value = ''
    parsedResume.value = null
    sessionId.value = ''
    stage.value = 'INIT'
    round.value = 0
    finished.value = false
    conversations.value = []
    report.value = null
    loading.value = false
    error.value = ''
  }

  return {
    resumeId,
    parsedResume,
    sessionId,
    stage,
    round,
    finished,
    conversations,
    report,
    loading,
    error,
    uploadResume,
    startInterview,
    sendAnswer,
    skipCurrentStage,
    jumpToFinalEvaluation,
    fetchReport,
    reset
  }
})
