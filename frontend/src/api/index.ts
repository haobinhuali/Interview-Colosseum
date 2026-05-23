import axios from 'axios'
import type { UploadResumeResponse, StartInterviewResponse, InterviewNextResponse, Report } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

export async function uploadResume(file: File): Promise<UploadResumeResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/upload-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function startInterview(resumeId: string, jobType: string): Promise<StartInterviewResponse> {
  const { data } = await api.post('/start-interview', { resume_id: resumeId, job_type: jobType })
  return data
}

export async function interviewNext(sessionId: string, userAnswer: string): Promise<InterviewNextResponse> {
  const { data } = await api.post('/interview-next', { session_id: sessionId, user_answer: userAnswer })
  return data
}

export async function skipStage(sessionId: string): Promise<InterviewNextResponse> {
  const { data } = await api.post('/skip-stage', { session_id: sessionId })
  return data
}

export async function jumpToFinal(sessionId: string): Promise<InterviewNextResponse> {
  const { data } = await api.post('/jump-to-final', { session_id: sessionId })
  return data
}

export async function generateReport(sessionId: string): Promise<{ report: Report }> {
  const { data } = await api.post('/generate-report', { session_id: sessionId })
  return data
}
