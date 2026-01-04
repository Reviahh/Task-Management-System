<script setup lang="ts">
import type { TaskSummary } from '../types/task'

defineProps<{
  summary: TaskSummary
}>()

const completionPercentage = (summary: TaskSummary) => {
  if (summary.total_tasks === 0) return 0
  return Math.round((summary.completed_tasks / summary.total_tasks) * 100)
}
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <!-- Total Tasks -->
    <div class="card p-5 group hover:border-primary-500/30 transition-colors">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
          <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
      </div>
      <div class="text-3xl font-display font-bold text-dark-100">{{ summary.total_tasks }}</div>
      <div class="text-sm text-dark-500">总任务数</div>
    </div>

    <!-- Completed -->
    <div class="card p-5 group hover:border-emerald-500/30 transition-colors">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
          <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <span class="text-xs font-mono text-emerald-400">{{ completionPercentage(summary) }}%</span>
      </div>
      <div class="text-3xl font-display font-bold text-emerald-400">{{ summary.completed_tasks }}</div>
      <div class="text-sm text-dark-500">已完成</div>
    </div>

    <!-- In Progress -->
    <div class="card p-5 group hover:border-blue-500/30 transition-colors">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
          <svg class="w-5 h-5 text-blue-400 animate-pulse-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>
      <div class="text-3xl font-display font-bold text-blue-400">{{ summary.in_progress_tasks }}</div>
      <div class="text-sm text-dark-500">进行中</div>
    </div>

    <!-- High Priority -->
    <div class="card p-5 group hover:border-red-500/30 transition-colors">
      <div class="flex items-center justify-between mb-3">
        <div class="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
          <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
      </div>
      <div class="text-3xl font-display font-bold text-red-400">{{ summary.high_priority_count }}</div>
      <div class="text-sm text-dark-500">高优先级</div>
    </div>
  </div>

  <!-- AI Summary -->
  <div v-if="summary.summary" class="card p-5 mt-4 bg-gradient-to-r from-accent-500/5 to-primary-500/5 border-accent-500/20">
    <div class="flex items-start gap-3">
      <div class="w-8 h-8 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      <div>
        <h4 class="text-sm font-medium text-accent-400 mb-1">AI 摘要</h4>
        <p class="text-sm text-dark-300 leading-relaxed">{{ summary.summary }}</p>
      </div>
    </div>
  </div>
</template>

