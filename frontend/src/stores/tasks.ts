import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, TaskCreate, TaskUpdate, TaskPriority, TaskStatus, TaskSummary } from '../types/task'
import * as api from '../api/tasks'

export const useTaskStore = defineStore('tasks', () => {
  // State
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(1)
  const summary = ref<TaskSummary | null>(null)
  
  // Filters
  const statusFilter = ref<TaskStatus | null>(null)
  const priorityFilter = ref<TaskPriority | null>(null)
  const searchQuery = ref('')
  const sortBy = ref('created_at')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // Computed
  const pendingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'pending')
  )
  
  const inProgressTasks = computed(() => 
    tasks.value.filter(t => t.status === 'in_progress')
  )
  
  const completedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'completed')
  )

  const highPriorityTasks = computed(() =>
    tasks.value.filter(t => t.priority === 'high')
  )

  // Actions
  async function fetchTasks() {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, any> = {
        page: page.value,
        page_size: pageSize.value,
        sort_by: sortBy.value,
        sort_order: sortOrder.value
      }
      
      if (statusFilter.value) params.status = statusFilter.value
      if (priorityFilter.value) params.priority = priorityFilter.value
      if (searchQuery.value) params.search = searchQuery.value
      
      const response = await api.getTasks(params)
      tasks.value = response.tasks
      total.value = response.total
      totalPages.value = response.total_pages
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch tasks'
      console.error('Error fetching tasks:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(id: number) {
    loading.value = true
    error.value = null
    try {
      currentTask.value = await api.getTask(id)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch task'
    } finally {
      loading.value = false
    }
  }

  async function createTask(taskData: TaskCreate): Promise<Task | null> {
    loading.value = true
    error.value = null
    try {
      const newTask = await api.createTask(taskData)
      tasks.value.unshift(newTask)
      total.value++
      return newTask
    } catch (e: any) {
      error.value = e.message || 'Failed to create task'
      return null
    } finally {
      loading.value = false
    }
  }

  async function createTaskFromNL(text: string): Promise<Task | null> {
    loading.value = true
    error.value = null
    try {
      const newTask = await api.createTaskFromText(text)
      tasks.value.unshift(newTask)
      total.value++
      return newTask
    } catch (e: any) {
      error.value = e.message || 'Failed to create task from text'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateTask(id: number, taskData: TaskUpdate): Promise<Task | null> {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await api.updateTask(id, taskData)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      if (currentTask.value?.id === id) {
        currentTask.value = updatedTask
      }
      return updatedTask
    } catch (e: any) {
      error.value = e.message || 'Failed to update task'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(id: number): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await api.deleteTask(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
      total.value--
      if (currentTask.value?.id === id) {
        currentTask.value = null
      }
      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to delete task'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary() {
    try {
      summary.value = await api.getTaskSummary()
    } catch (e: any) {
      console.error('Error fetching summary:', e)
    }
  }

  function setFilters(filters: {
    status?: TaskStatus | null
    priority?: TaskPriority | null
    search?: string
  }) {
    if (filters.status !== undefined) statusFilter.value = filters.status
    if (filters.priority !== undefined) priorityFilter.value = filters.priority
    if (filters.search !== undefined) searchQuery.value = filters.search
    page.value = 1
  }

  function setSort(field: string, order: 'asc' | 'desc') {
    sortBy.value = field
    sortOrder.value = order
    page.value = 1
  }

  function setPage(newPage: number) {
    page.value = newPage
  }

  function clearFilters() {
    statusFilter.value = null
    priorityFilter.value = null
    searchQuery.value = ''
    page.value = 1
  }

  return {
    // State
    tasks,
    currentTask,
    loading,
    error,
    total,
    page,
    pageSize,
    totalPages,
    summary,
    statusFilter,
    priorityFilter,
    searchQuery,
    sortBy,
    sortOrder,
    
    // Computed
    pendingTasks,
    inProgressTasks,
    completedTasks,
    highPriorityTasks,
    
    // Actions
    fetchTasks,
    fetchTask,
    createTask,
    createTaskFromNL,
    updateTask,
    deleteTask,
    fetchSummary,
    setFilters,
    setSort,
    setPage,
    clearFilters
  }
})

