<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTaskStore } from '../stores/tasks'
import type { TaskPriority, TaskStatus } from '../types/task'
import { useDebounceFn } from '@vueuse/core'

const store = useTaskStore()
const searchInput = ref(store.searchQuery)

const debouncedSearch = useDebounceFn((value: string) => {
  store.setFilters({ search: value })
}, 300)

watch(searchInput, (value) => {
  debouncedSearch(value)
})

const statusOptions: { value: TaskStatus | ''; label: string }[] = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '待处理' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' }
]

const priorityOptions: { value: TaskPriority | ''; label: string }[] = [
  { value: '', label: '全部优先级' },
  { value: 'high', label: '高优先级' },
  { value: 'medium', label: '中优先级' },
  { value: 'low', label: '低优先级' }
]

const sortOptions = [
  { value: 'created_at', label: '创建时间' },
  { value: 'updated_at', label: '更新时间' },
  { value: 'priority', label: '优先级' },
  { value: 'title', label: '标题' }
]

function handleStatusChange(status: string) {
  store.setFilters({ status: status ? status as TaskStatus : null })
}

function handlePriorityChange(priority: string) {
  store.setFilters({ priority: priority ? priority as TaskPriority : null })
}

function handleSortChange(event: Event) {
  const target = event.target as HTMLSelectElement
  store.setSort(target.value, store.sortOrder)
}

function toggleSortOrder() {
  store.setSort(store.sortBy, store.sortOrder === 'asc' ? 'desc' : 'asc')
}

function clearAll() {
  searchInput.value = ''
  store.clearFilters()
}

const hasFilters = ref(false)
watch([
  () => store.statusFilter,
  () => store.priorityFilter,
  () => store.searchQuery
], () => {
  hasFilters.value = !!(store.statusFilter || store.priorityFilter || store.searchQuery)
}, { immediate: true })
</script>

<template>
  <div class="card p-4">
    <div class="flex flex-col lg:flex-row gap-4">
      <!-- Search -->
      <div class="relative flex-1">
        <svg 
          class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" 
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          v-model="searchInput"
          type="text"
          class="input pl-12"
          placeholder="搜索任务..."
        />
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-3">
        <select 
          :value="store.statusFilter || ''"
          @change="handleStatusChange(($event.target as HTMLSelectElement).value)"
          class="input w-auto min-w-[140px]"
        >
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>

        <select 
          :value="store.priorityFilter || ''"
          @change="handlePriorityChange(($event.target as HTMLSelectElement).value)"
          class="input w-auto min-w-[140px]"
        >
          <option v-for="opt in priorityOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>

        <!-- Sort -->
        <div class="flex gap-1">
          <select 
            :value="store.sortBy"
            @change="handleSortChange"
            class="input w-auto min-w-[120px] rounded-r-none border-r-0"
          >
            <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
          <button 
            @click="toggleSortOrder"
            class="btn-ghost rounded-l-none px-3"
            :title="store.sortOrder === 'asc' ? '升序' : '降序'"
          >
            <svg 
              class="w-5 h-5 transition-transform duration-200" 
              :class="{ 'rotate-180': store.sortOrder === 'asc' }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        <!-- Clear Filters -->
        <button 
          v-if="hasFilters"
          @click="clearAll"
          class="btn-ghost text-red-400 hover:text-red-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          清除
        </button>
      </div>
    </div>

    <!-- Active filters display -->
    <div v-if="hasFilters" class="mt-3 flex items-center gap-2 text-sm">
      <span class="text-dark-500">筛选:</span>
      <span v-if="store.searchQuery" class="tag-primary">
        搜索: {{ store.searchQuery }}
      </span>
      <span v-if="store.statusFilter" class="tag">
        {{ statusOptions.find(s => s.value === store.statusFilter)?.label }}
      </span>
      <span v-if="store.priorityFilter" class="tag">
        {{ priorityOptions.find(p => p.value === store.priorityFilter)?.label }}
      </span>
      <span class="text-dark-500 ml-2">
        共 {{ store.total }} 条结果
      </span>
    </div>
  </div>
</template>

