import axios from 'axios'
import type { 
  Task, 
  TaskCreate, 
  TaskUpdate, 
  TaskListResponse, 
  ParsedTask,
  TaskBreakdown,
  SemanticSearchResult,
  TaskSummary
} from '../types/task'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Task CRUD
export async function getTasks(params: {
  page?: number
  page_size?: number
  status?: string
  priority?: string
  search?: string
  sort_by?: string
  sort_order?: string
} = {}): Promise<TaskListResponse> {
  const { data } = await api.get('/tasks/', { params })
  return data
}

export async function getTask(id: number): Promise<Task> {
  const { data } = await api.get(`/tasks/${id}`)
  return data
}

export async function createTask(task: TaskCreate): Promise<Task> {
  const { data } = await api.post('/tasks/', task)
  return data
}

export async function updateTask(id: number, task: TaskUpdate): Promise<Task> {
  const { data } = await api.put(`/tasks/${id}`, task)
  return data
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`/tasks/${id}`)
}

// AI Features
export async function parseNaturalLanguage(text: string): Promise<ParsedTask> {
  const { data } = await api.post('/tasks/ai/parse', { text })
  return data
}

export async function createTaskFromText(text: string): Promise<Task> {
  const { data } = await api.post('/tasks/ai/create-from-text', { text })
  return data
}

export async function suggestTags(taskId: number): Promise<{ task_id: number; suggested_tags: string[]; reasoning: string }> {
  const { data } = await api.post(`/tasks/${taskId}/ai/suggest-tags`)
  return data
}

export async function suggestPriority(taskId: number): Promise<{ task_id: number; suggested_priority: string; reasoning: string }> {
  const { data } = await api.post(`/tasks/${taskId}/ai/suggest-priority`)
  return data
}

export async function breakdownTask(taskId: number): Promise<TaskBreakdown> {
  const { data } = await api.post(`/tasks/${taskId}/ai/breakdown`)
  return data
}

export async function semanticSearch(query: string, limit: number = 10): Promise<{ results: SemanticSearchResult[]; query: string }> {
  const { data } = await api.post('/tasks/ai/semantic-search', { query, limit })
  return data
}

export async function getTaskSummary(taskIds?: number[], period?: string): Promise<TaskSummary> {
  const { data } = await api.post('/tasks/ai/summary', { task_ids: taskIds, period })
  return data
}

// Find similar tasks
export async function findSimilarTasks(taskId: number, limit: number = 5): Promise<{
  source_task_id: number
  similar_tasks: Array<{ task: Task; similarity_score: number }>
}> {
  const { data } = await api.post('/tasks/ai/similar', { task_id: taskId, limit })
  return data
}

// Categorize task
export async function categorizeTask(title: string, description?: string): Promise<{
  category: string
  subcategories: string[]
  reasoning: string
}> {
  const { data } = await api.post('/tasks/ai/categorize', { title, description })
  return data
}

// Get task insights
export async function getTaskInsights(): Promise<{
  total: number
  by_status: Record<string, number>
  by_priority: Record<string, number>
  by_tag: Record<string, number>
  completion_rate: number
  insights: string[]
  recommendations: string[]
}> {
  const { data } = await api.get('/tasks/ai/insights')
  return data
}

// Health check
export async function checkHealth(): Promise<{ status: string; ai_available: boolean }> {
  const { data } = await api.get('/health')
  return data
}

