<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <nav class="border-b border-gray-800 px-6 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <h1
          class="text-xl font-bold cursor-pointer hover:text-blue-400 transition-colors"
          @click="router.push('/')"
        >
          ⚔️ Interview Colosseum
        </h1>
        <span class="text-sm text-gray-400">面试角斗场</span>
      </div>
    </nav>
    <main class="max-w-6xl mx-auto px-6 py-8">
      <router-view />
    </main>
  </div>
</template>
