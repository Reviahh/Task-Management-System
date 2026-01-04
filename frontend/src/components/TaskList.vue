<script setup lang="ts">
import { ref } from 'vue'
import { useTaskStore } from '../stores/tasks'
import type { Task, TaskStatus } from '../types/task'
import * as api from '../api/tasks'

const props = defineProps<{
  tasks: Task[]
}>()

const emit = defineEmits<{
  edit: [taskId: number]
  refresh: []
}>()

const store = useTaskStore()
const expandedTask = ref<number | null>(null)
const breakdownLoading = ref<number | null>(null)
const breakdown = ref<{ subtasks: any[]; reasoning: string } | null>(null)

const statusLabels: Record<TaskStatus, string> = {
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成'
}

const priorityLabels = {
  low: '低',
  medium: '中',
  high: '高'
}

function toggleExpand(taskId: number) {
  expandedTask.value = expandedTask.value === taskId ? null : taskId
  breakdown.value = null
}

async function handleStatusChange(task: Task, newStatus: TaskStatus) {
  await store.updateTask(task.id, { status: newStatus })
  await store.fetchSummary()
}

async function handleDelete(taskId: number) {
  if (confirm('确定要删除这个任务吗？')) {
    await store.deleteTask(taskId)
    await store.fetchSummary()
  }
}

async function handleBreakdown(taskId: number) {
  breakdownLoading.value = taskId
  try {
    const result = await api.breakdownTask(taskId)
    breakdown.value = {
      subtasks: result.subtasks,
      reasoning: result.reasoning || ''
    }
  } catch (e) {
    console.error('Breakdown error:', e)
  } finally {
    breakdownLoading.value = null
  }
}

async function createSubtask(subtask: { title: string; description?: string }) {
  await store.createTask({
    title: subtask.title,
    description: subtask.description,
    status: 'pending',
    priority: 'medium'
  })
  emit('refresh')
}
</script>

<template>
  <div class="space-y-4">
    <TransitionGroup name="list">
      <div 
        v-for="task in tasks" 
        :key="task.id"
        class="card-hover overflow-hidden"
      >
        <!-- Task Header -->
        <div class="p-5">
          <div class="flex items-start gap-4">
            <!-- Status Checkbox -->
            <button 
              @click="handleStatusChange(task, task.status === 'completed' ? 'pending' : 'completed')"
              :class="[
                'w-6 h-6 rounded-lg border-2 flex-shrink-0 flex items-center justify-center transition-all duration-200 mt-0.5',
                task.status === 'completed' 
                  ? 'bg-emerald-500 border-emerald-500' 
                  : 'border-dark-600 hover:border-primary-500'
              ]"
            >
              <svg v-if="task.status === 'completed'" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
              </svg>
            </button>

            <!-- Task Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-2">
                <h3 
                  :class="[
                    'text-lg font-medium truncate',
                    task.status === 'completed' ? 'text-dark-500 line-through' : 'text-dark-100'
                  ]"
                >
                  {{ task.title }}
                </h3>
              </div>

              <p v-if="task.description" class="text-sm text-dark-400 mb-3 line-clamp-2">
                {{ task.description }}
              </p>

              <!-- Tags & Meta -->
              <div class="flex flex-wrap items-center gap-2">
                <span :class="['tag', `priority-${task.priority}`]">
                  {{ priorityLabels[task.priority] }}优先级
                </span>
                <span :class="['tag', `status-${task.status}`]">
                  {{ statusLabels[task.status] }}
                </span>
                <span 
                  v-for="tag in task.tags" 
                  :key="tag" 
                  class="tag-primary"
                >
                  {{ tag }}
                </span>
              </div>

              <!-- AI Suggestions -->
              <div v-if="task.ai_suggested_tags?.length || task.ai_suggested_priority" class="mt-3 flex items-center gap-2">
                <span class="text-xs text-accent-400 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI建议:
                </span>
                <span 
                  v-for="tag in task.ai_suggested_tags" 
                  :key="tag" 
                  class="tag-accent text-xs"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 flex-shrink-0">
              <button 
                @click="toggleExpand(task.id)"
                :class="[
                  'p-2 rounded-lg transition-all duration-200',
                  expandedTask === task.id 
                    ? 'bg-primary-500/20 text-primary-400' 
                    : 'hover:bg-dark-800 text-dark-400 hover:text-dark-200'
                ]"
                title="展开详情"
              >
                <svg 
                  class="w-5 h-5 transition-transform duration-200" 
                  :class="{ 'rotate-180': expandedTask === task.id }"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <button 
                @click="emit('edit', task.id)"
                class="p-2 rounded-lg hover:bg-dark-800 text-dark-400 hover:text-dark-200 transition-colors"
                title="编辑"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button 
                @click="handleDelete(task.id)"
                class="p-2 rounded-lg hover:bg-red-500/10 text-dark-400 hover:text-red-400 transition-colors"
                title="删除"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Expanded Content -->
        <Transition name="expand">
          <div v-if="expandedTask === task.id" class="border-t border-dark-800 bg-dark-900/50">
            <div class="p-5 space-y-4">
              <!-- Status Change Buttons -->
              <div class="flex flex-wrap gap-2">
                <span class="text-sm text-dark-400 mr-2">状态:</span>
                <button 
                  v-for="status in (['pending', 'in_progress', 'completed'] as TaskStatus[])"
                  :key="status"
                  @click="handleStatusChange(task, status)"
                  :class="[
                    'px-3 py-1 rounded-lg text-sm transition-all',
                    task.status === status 
                      ? `status-${status} border` 
                      : 'bg-dark-800 text-dark-400 hover:bg-dark-700'
                  ]"
                >
                  {{ statusLabels[status] }}
                </button>
              </div>

              <!-- Task Info -->
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-dark-500">创建时间:</span>
                  <span class="text-dark-300 ml-2">{{ new Date(task.created_at).toLocaleString('zh-CN') }}</span>
                </div>
                <div>
                  <span class="text-dark-500">更新时间:</span>
                  <span class="text-dark-300 ml-2">{{ new Date(task.updated_at).toLocaleString('zh-CN') }}</span>
                </div>
              </div>

              <!-- AI Breakdown -->
              <div class="pt-4 border-t border-dark-800">
                <button 
                  @click="handleBreakdown(task.id)"
                  :disabled="breakdownLoading === task.id"
                  class="btn-accent text-sm flex items-center gap-2"
                >
                  <svg v-if="breakdownLoading === task.id" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI 任务分解
                </button>

                <!-- Breakdown Results -->
                <div v-if="breakdown && expandedTask === task.id" class="mt-4 space-y-3">
                  <p v-if="breakdown.reasoning" class="text-sm text-accent-400 italic">
                    {{ breakdown.reasoning }}
                  </p>
                  <div 
                    v-for="subtask in breakdown.subtasks" 
                    :key="subtask.order"
                    class="flex items-center gap-3 p-3 bg-dark-800/50 rounded-lg group"
                  >
                    <span class="w-6 h-6 rounded-full bg-accent-500/20 text-accent-400 text-sm flex items-center justify-center flex-shrink-0">
                      {{ subtask.order }}
                    </span>
                    <div class="flex-1 min-w-0">
                      <p class="text-dark-200 font-medium">{{ subtask.title }}</p>
                      <p v-if="subtask.description" class="text-sm text-dark-500">{{ subtask.description }}</p>
                      <span v-if="subtask.estimated_effort" class="text-xs text-dark-500">
                        预计: {{ subtask.estimated_effort }}
                      </span>
                    </div>
                    <button 
                      @click="createSubtask(subtask)"
                      class="opacity-0 group-hover:opacity-100 p-2 rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-all"
                      title="创建为新任务"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

