export interface ParsedResume {
  name: string
  skills: string[]
  projects: Project[]
}

export interface Project {
  name: string
  description: string
  tech_stack: string[]
}

export interface UploadResumeResponse {
  resume_id: string
  parsed_data: ParsedResume
}

export interface StartInterviewResponse {
  session_id: string
  stage: string
  first_message: string
  thinking: string[]
}

export interface InterviewNextResponse {
  message: string
  thinking: string[]
  stage: string
  round: number
  finished: boolean
  should_handover: boolean
}

export interface RadarItem {
  dim: string
  score: number
}

export interface Suggestion {
  title: string
  content: string
  evidence: string
}

export interface Report {
  summary: string
  scores: Record<string, number>
  radar_data: RadarItem[]
  suggestions: Suggestion[]
  weighted_total: number
}

export interface ChatMessage {
  role: 'interviewer' | 'candidate' | 'system'
  content: string
  stage: string
  thinking?: string[]
}

export type StageType = 'INIT' | 'TECH' | 'PRESSURE' | 'COMPREHENSIVE' | 'DONE'
