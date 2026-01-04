export type TaskStatus = 'pending' | 'in_progress' | 'completed'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Task {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  tags: string[]
  created_at: string
  updated_at: string
  ai_suggested_tags: string[]
  ai_suggested_priority: string | null
}

export interface TaskCreate {
  title: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  tags?: string[]
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  tags?: string[]
}

export interface TaskListResponse {
  tasks: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ParsedTask {
  title: string
  description: string | null
  priority: TaskPriority
  tags: string[]
  due_date: string | null
  confidence: number
}

export interface SubTask {
  title: string
  description: string | null
  estimated_effort: string | null
  order: number
}

export interface TaskBreakdown {
  original_task_id: number
  subtasks: SubTask[]
  reasoning: string | null
}

export interface SemanticSearchResult {
  task: Task
  similarity_score: number
}

export interface TaskSummary {
  summary: string
  total_tasks: number
  completed_tasks: number
  pending_tasks: number
  in_progress_tasks: number
  high_priority_count: number
}

