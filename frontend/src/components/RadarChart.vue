<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { RadarItem } from '../types'

const props = defineProps<{
  data: RadarItem[]
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value || !props.data.length) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const indicator = props.data.map(item => ({
    name: item.dim,
    max: 10
  }))

  const values = props.data.map(item => item.score)

  chart.setOption({
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator,
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#9ca3af',
        fontSize: 13
      },
      splitLine: {
        lineStyle: {
          color: '#374151'
        }
      },
      splitArea: {
        areaStyle: {
          color: ['#1f2937', '#111827']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#374151'
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: values,
            name: '能力评估',
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.3)'
            },
            lineStyle: {
              color: '#3b82f6',
              width: 2
            },
            itemStyle: {
              color: '#3b82f6'
            }
          }
        ]
      }
    ]
  })
}

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })
</script>

<template>
  <div ref="chartRef" class="w-full h-80" />
</template>
