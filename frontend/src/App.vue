<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useTaskStore } from './stores/tasks'
import TaskList from './components/TaskList.vue'
import TaskForm from './components/TaskForm.vue'
import AIFeatures from './components/AIFeatures.vue'
import FilterBar from './components/FilterBar.vue'
import TaskSummary from './components/TaskSummary.vue'

const store = useTaskStore()
const showTaskForm = ref(false)
const editingTask = ref<number | null>(null)
const activeTab = ref<'list' | 'ai'>('list')

onMounted(async () => {
  await Promise.all([
    store.fetchTasks(),
    store.fetchSummary()
  ])
})

watch([
  () => store.statusFilter,
  () => store.priorityFilter,
  () => store.searchQuery,
  () => store.sortBy,
  () => store.sortOrder,
  () => store.page
], () => {
  store.fetchTasks()
}, { deep: true })

function handleCreateTask() {
  editingTask.value = null
  showTaskForm.value = true
}

function handleEditTask(taskId: number) {
  editingTask.value = taskId
  showTaskForm.value = true
}

function handleCloseForm() {
  showTaskForm.value = false
  editingTask.value = null
}

async function handleTaskSaved() {
  showTaskForm.value = false
  editingTask.value = null
  await store.fetchTasks()
  await store.fetchSummary()
}
</script>

<template>
  <div class="min-h-screen" role="application" aria-label="智能任务管理系统">
    <!-- Skip Link for Accessibility -->
    <a 
      href="#main-content" 
      class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-primary-500 focus:text-white focus:rounded-lg"
    >
      跳转到主要内容
    </a>

    <!-- Header -->
    <header class="glass sticky top-0 z-50" role="banner">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center glow" aria-hidden="true">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
            </div>
            <div>
              <h1 class="text-xl font-display font-bold text-gradient">智能任务管理</h1>
              <p class="text-xs text-dark-400">AI-Powered Task Management</p>
            </div>
          </div>
          
          <button 
            @click="handleCreateTask" 
            class="btn-primary flex items-center gap-2"
            aria-label="新建任务"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="hidden sm:inline">新建任务</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" role="main">
      <!-- Tab Navigation -->
      <nav class="flex gap-2 mb-8" role="tablist" aria-label="功能导航">
        <button 
          @click="activeTab = 'list'"
          role="tab"
          :aria-selected="activeTab === 'list'"
          aria-controls="tab-panel-list"
          :tabindex="activeTab === 'list' ? 0 : -1"
          :class="[
            'px-6 py-3 rounded-xl font-medium transition-all duration-300',
            activeTab === 'list' 
              ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
              : 'bg-dark-800/50 text-dark-400 border border-dark-700 hover:bg-dark-800'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            任务列表
          </span>
        </button>
        <button 
          @click="activeTab = 'ai'"
          role="tab"
          :aria-selected="activeTab === 'ai'"
          aria-controls="tab-panel-ai"
          :tabindex="activeTab === 'ai' ? 0 : -1"
          :class="[
            'px-6 py-3 rounded-xl font-medium transition-all duration-300',
            activeTab === 'ai' 
              ? 'bg-accent-500/20 text-accent-400 border border-accent-500/30' 
              : 'bg-dark-800/50 text-dark-400 border border-dark-700 hover:bg-dark-800'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI 助手
          </span>
        </button>
      </nav>

      <!-- Summary Cards -->
      <TaskSummary v-if="store.summary" :summary="store.summary" class="mb-8" />

      <!-- Content Area -->
      <div 
        v-if="activeTab === 'list'" 
        id="tab-panel-list"
        role="tabpanel"
        aria-labelledby="tab-list"
        class="animate-fade-in"
      >
        <FilterBar class="mb-6" />
        
        <div v-if="store.loading && store.tasks.length === 0" class="card p-12 text-center" role="status" aria-live="polite">
          <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" aria-hidden="true"></div>
          <p class="text-dark-400">加载中...</p>
        </div>
        
        <div v-else-if="store.error" class="card p-12 text-center" role="alert" aria-live="assertive">
          <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4" aria-hidden="true">
            <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-red-400">{{ store.error }}</p>
          <button @click="store.fetchTasks" class="btn-ghost mt-4" aria-label="重试加载任务">重试</button>
        </div>
        
        <div v-else-if="store.tasks.length === 0" class="card p-12 text-center">
          <div class="w-20 h-20 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4" aria-hidden="true">
            <svg class="w-10 h-10 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 class="text-lg font-medium text-dark-200 mb-2">暂无任务</h3>
          <p class="text-dark-500 mb-6">点击上方按钮创建你的第一个任务</p>
          <button @click="handleCreateTask" class="btn-primary" aria-label="创建第一个任务">创建任务</button>
        </div>
        
        <TaskList 
          v-else
          :tasks="store.tasks" 
          @edit="handleEditTask"
          @refresh="store.fetchTasks"
        />

        <!-- Pagination -->
        <nav v-if="store.totalPages > 1" class="flex justify-center gap-2 mt-8" role="navigation" aria-label="分页导航">
          <button 
            @click="store.setPage(store.page - 1)"
            :disabled="store.page <= 1"
            class="btn-ghost px-3 py-2"
            aria-label="上一页"
            :aria-disabled="store.page <= 1"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <span class="px-4 py-2 text-dark-400" aria-live="polite" aria-atomic="true">
            第 {{ store.page }} / {{ store.totalPages }} 页
          </span>
          
          <button 
            @click="store.setPage(store.page + 1)"
            :disabled="store.page >= store.totalPages"
            class="btn-ghost px-3 py-2"
            aria-label="下一页"
            :aria-disabled="store.page >= store.totalPages"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </nav>
      </div>

      <div 
        v-else 
        id="tab-panel-ai"
        role="tabpanel"
        aria-labelledby="tab-ai"
      >
        <AIFeatures class="animate-fade-in" @task-created="handleTaskSaved" />
      </div>
    </main>

    <!-- Task Form Modal -->
    <Teleport to="body">
      <div 
        v-if="showTaskForm" 
        class="fixed inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        role="dialog"
        aria-modal="true"
        :aria-label="editingTask ? '编辑任务' : '新建任务'"
        @click.self="handleCloseForm"
        @keydown.escape="handleCloseForm"
      >
        <div class="card w-full max-w-lg animate-scale-in" role="document">
          <TaskForm 
            :task-id="editingTask"
            @close="handleCloseForm"
            @saved="handleTaskSaved"
          />
        </div>
      </div>
    </Teleport>

    <!-- Screen Reader Announcements -->
    <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">
      <span v-if="store.loading">正在加载任务...</span>
    </div>
  </div>
</template>

