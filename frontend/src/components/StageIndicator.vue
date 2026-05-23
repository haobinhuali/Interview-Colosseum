<script setup lang="ts">
import type { StageType } from '../types'

const props = defineProps<{
  currentStage: StageType
  round: number
  maxRounds: number
}>()

const stages = [
  { key: 'TECH', label: '技术面', icon: '🔵', color: 'text-blue-400' },
  { key: 'PRESSURE', label: '压力面', icon: '🔴', color: 'text-red-400' },
  { key: 'COMPREHENSIVE', label: '综合面', icon: '🟢', color: 'text-green-400' }
]

function getStageStatus(stageKey: string): 'completed' | 'active' | 'pending' {
  const order = ['TECH', 'PRESSURE', 'COMPREHENSIVE']
  const currentIdx = order.indexOf(props.currentStage)
  const stageIdx = order.indexOf(stageKey)
  if (stageIdx < currentIdx || props.currentStage === 'DONE') return 'completed'
  if (stageIdx === currentIdx) return 'active'
  return 'pending'
}
</script>

<template>
  <div class="flex items-center justify-center gap-4 py-4">
    <template v-for="(stage, index) in stages" :key="stage.key">
      <div class="flex items-center gap-2">
        <div
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300',
            getStageStatus(stage.key) === 'active'
              ? 'bg-gray-700 ring-2 ring-blue-500 scale-105'
              : getStageStatus(stage.key) === 'completed'
                ? 'bg-gray-800 text-gray-400'
                : 'bg-gray-800/50 text-gray-600'
          ]"
        >
          <span>{{ stage.icon }}</span>
          <span :class="getStageStatus(stage.key) === 'active' ? stage.color : ''">{{ stage.label }}</span>
          <span
            v-if="getStageStatus(stage.key) === 'active'"
            class="text-xs text-gray-400 ml-1"
          >
            ({{ round }}/{{ maxRounds }})
          </span>
          <span v-if="getStageStatus(stage.key) === 'completed'" class="text-green-500">✓</span>
        </div>
        <div
          v-if="index < stages.length - 1"
          :class="[
            'w-8 h-0.5',
            getStageStatus(stage.key) === 'completed' ? 'bg-green-500' : 'bg-gray-700'
          ]"
        />
      </div>
    </template>
  </div>
</template>
