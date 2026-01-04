<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTaskStore } from '../stores/tasks'
import * as api from '../api/tasks'
import type { ParsedTask, SemanticSearchResult } from '../types/task'

const emit = defineEmits<{
  'task-created': []
}>()

const store = useTaskStore()

// Natural Language Input
const nlInput = ref('')
const nlLoading = ref(false)
const parsedTask = ref<ParsedTask | null>(null)

// Semantic Search
const searchQuery = ref('')
const searchLoading = ref(false)
const searchResults = ref<SemanticSearchResult[]>([])

// Task Categorization
const catTitle = ref('')
const catDescription = ref('')
const catLoading = ref(false)
const catResult = ref<{ category: string; subcategories: string[]; reasoning: string } | null>(null)

// Task Insights
const insights = ref<{
  total: number
  by_status: Record<string, number>
  by_priority: Record<string, number>
  completion_rate: number
  insights: string[]
  recommendations: string[]
} | null>(null)
const insightsLoading = ref(false)

const priorityLabels: Record<string, string> = {
  low: '低',
  medium: '中',
  high: '高'
}

const statusLabels: Record<string, string> = {
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成'
}

const categoryLabels: Record<string, string> = {
  work: '工作',
  personal: '个人',
  health: '健康',
  finance: '财务',
  learning: '学习',
  social: '社交',
  home: '家庭',
  creative: '创意',
  urgent: '紧急',
  other: '其他'
}

async function handleNLParse() {
  if (!nlInput.value.trim()) return
  
  nlLoading.value = true
  parsedTask.value = null
  try {
    parsedTask.value = await api.parseNaturalLanguage(nlInput.value)
  } catch (e) {
    console.error('Parse error:', e)
  } finally {
    nlLoading.value = false
  }
}

async function createFromParsed() {
  if (!parsedTask.value) return
  
  nlLoading.value = true
  try {
    await store.createTask({
      title: parsedTask.value.title,
      description: parsedTask.value.description || undefined,
      priority: parsedTask.value.priority,
      tags: parsedTask.value.tags
    })
    nlInput.value = ''
    parsedTask.value = null
    emit('task-created')
  } catch (e) {
    console.error('Create error:', e)
  } finally {
    nlLoading.value = false
  }
}

async function createDirectly() {
  if (!nlInput.value.trim()) return
  
  nlLoading.value = true
  try {
    await store.createTaskFromNL(nlInput.value)
    nlInput.value = ''
    parsedTask.value = null
    emit('task-created')
  } catch (e) {
    console.error('Create error:', e)
  } finally {
    nlLoading.value = false
  }
}

async function handleSemanticSearch() {
  if (!searchQuery.value.trim()) return
  
  searchLoading.value = true
  searchResults.value = []
  try {
    const response = await api.semanticSearch(searchQuery.value)
    searchResults.value = response.results
  } catch (e) {
    console.error('Search error:', e)
  } finally {
    searchLoading.value = false
  }
}

function clearResults() {
  searchResults.value = []
  searchQuery.value = ''
}

async function handleCategorize() {
  if (!catTitle.value.trim()) return
  
  catLoading.value = true
  catResult.value = null
  try {
    catResult.value = await api.categorizeTask(catTitle.value, catDescription.value || undefined)
  } catch (e) {
    console.error('Categorize error:', e)
  } finally {
    catLoading.value = false
  }
}

async function loadInsights() {
  insightsLoading.value = true
  try {
    insights.value = await api.getTaskInsights()
  } catch (e) {
    console.error('Insights error:', e)
  } finally {
    insightsLoading.value = false
  }
}

onMounted(() => {
  loadInsights()
})
</script>

<template>
  <div class="space-y-8">
    <!-- Natural Language Task Creation -->
    <div class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-500 to-accent-600 flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-display font-bold text-dark-100">自然语言创建任务</h2>
          <p class="text-sm text-dark-400">用自然语言描述任务，AI 会自动解析</p>
        </div>
      </div>

      <div class="space-y-4">
        <div class="relative">
          <textarea 
            v-model="nlInput"
            class="input-lg min-h-[120px] resize-none pr-32"
            placeholder="例如：明天下午3点提醒我去买菜，这很重要..."
            @keydown.enter.meta="createDirectly"
            @keydown.enter.ctrl="createDirectly"
          ></textarea>
          <div class="absolute bottom-3 right-3 flex gap-2">
            <button 
              @click="handleNLParse"
              :disabled="!nlInput.trim() || nlLoading"
              class="btn-ghost text-sm"
            >
              预览
            </button>
            <button 
              @click="createDirectly"
              :disabled="!nlInput.trim() || nlLoading"
              class="btn-accent text-sm"
            >
              <svg v-if="nlLoading" class="w-4 h-4 animate-spin mr-1" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              创建
            </button>
          </div>
        </div>

        <!-- Parsed Preview -->
        <Transition name="fade">
          <div v-if="parsedTask" class="p-4 bg-accent-500/5 border border-accent-500/20 rounded-xl space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-accent-400">AI 解析结果</span>
              <span class="text-xs text-dark-500">
                置信度: {{ (parsedTask.confidence * 100).toFixed(0) }}%
              </span>
            </div>
            
            <div class="space-y-2">
              <div class="flex items-start gap-2">
                <span class="text-dark-500 text-sm min-w-[60px]">标题:</span>
                <span class="text-dark-200">{{ parsedTask.title }}</span>
              </div>
              <div v-if="parsedTask.description" class="flex items-start gap-2">
                <span class="text-dark-500 text-sm min-w-[60px]">描述:</span>
                <span class="text-dark-300 text-sm">{{ parsedTask.description }}</span>
              </div>
              <div class="flex items-center gap-4">
                <div class="flex items-center gap-2">
                  <span class="text-dark-500 text-sm">优先级:</span>
                  <span :class="['tag', `priority-${parsedTask.priority}`]">
                    {{ priorityLabels[parsedTask.priority] }}
                  </span>
                </div>
                <div v-if="parsedTask.due_date" class="flex items-center gap-2">
                  <span class="text-dark-500 text-sm">截止:</span>
                  <span class="text-dark-300 text-sm">{{ parsedTask.due_date }}</span>
                </div>
              </div>
              <div v-if="parsedTask.tags.length" class="flex items-center gap-2 flex-wrap">
                <span class="text-dark-500 text-sm">标签:</span>
                <span v-for="tag in parsedTask.tags" :key="tag" class="tag-primary text-xs">
                  {{ tag }}
                </span>
              </div>
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button @click="parsedTask = null" class="btn-ghost text-sm">取消</button>
              <button @click="createFromParsed" class="btn-primary text-sm">确认创建</button>
            </div>
          </div>
        </Transition>

        <!-- Examples -->
        <div class="flex flex-wrap gap-2 pt-2">
          <span class="text-xs text-dark-500">示例:</span>
          <button 
            v-for="example in [
              '紧急：修复生产环境的登录bug',
              '下周一之前完成项目文档',
              '研究新的AI框架，空闲时处理'
            ]"
            :key="example"
            @click="nlInput = example"
            class="text-xs px-2 py-1 rounded-lg bg-dark-800/50 text-dark-400 hover:bg-dark-800 hover:text-dark-300 transition-colors"
          >
            {{ example }}
          </button>
        </div>
      </div>
    </div>

    <!-- Semantic Search -->
    <div class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-display font-bold text-dark-100">语义搜索</h2>
          <p class="text-sm text-dark-400">通过含义搜索任务，而非仅关键词匹配</p>
        </div>
      </div>

      <div class="space-y-4">
        <div class="flex gap-3">
          <div class="relative flex-1">
            <svg 
              class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" 
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input 
              v-model="searchQuery"
              type="text"
              class="input pl-12"
              placeholder="描述你想找的任务..."
              @keydown.enter="handleSemanticSearch"
            />
          </div>
          <button 
            @click="handleSemanticSearch"
            :disabled="!searchQuery.trim() || searchLoading"
            class="btn-primary"
          >
            <svg v-if="searchLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span v-else>搜索</span>
          </button>
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length" class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-dark-400">找到 {{ searchResults.length }} 个相关任务</span>
            <button @click="clearResults" class="text-xs text-dark-500 hover:text-dark-300">
              清除结果
            </button>
          </div>
          
          <TransitionGroup name="list" tag="div" class="space-y-2">
            <div 
              v-for="result in searchResults" 
              :key="result.task.id"
              class="p-4 bg-dark-800/50 rounded-xl border border-dark-700 hover:border-primary-500/30 transition-colors"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <h4 class="font-medium text-dark-200 truncate">{{ result.task.title }}</h4>
                  <p v-if="result.task.description" class="text-sm text-dark-500 mt-1 line-clamp-2">
                    {{ result.task.description }}
                  </p>
                  <div class="flex items-center gap-2 mt-2">
                    <span :class="['tag text-xs', `priority-${result.task.priority}`]">
                      {{ priorityLabels[result.task.priority] }}
                    </span>
                    <span v-for="tag in result.task.tags.slice(0, 3)" :key="tag" class="tag-primary text-xs">
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="text-right flex-shrink-0">
                  <div class="text-sm font-mono text-primary-400">
                    {{ (result.similarity_score * 100).toFixed(0) }}%
                  </div>
                  <div class="text-xs text-dark-500">相似度</div>
                </div>
              </div>
            </div>
          </TransitionGroup>
        </div>

        <!-- Empty State -->
        <div v-else-if="searchQuery && !searchLoading" class="text-center py-8 text-dark-500">
          <svg class="w-12 h-12 mx-auto mb-3 text-dark-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>输入搜索词开始查找</p>
        </div>
      </div>
    </div>

    <!-- Task Categorization -->
    <div class="card p-6">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-display font-bold text-dark-100">智能任务分类</h2>
          <p class="text-sm text-dark-400">AI 自动分析并分类你的任务</p>
        </div>
      </div>

      <div class="space-y-4">
        <input 
          v-model="catTitle"
          type="text"
          class="input"
          placeholder="输入任务标题..."
        />
        <textarea 
          v-model="catDescription"
          class="input min-h-[80px] resize-none"
          placeholder="可选：添加任务描述..."
        ></textarea>
        <button 
          @click="handleCategorize"
          :disabled="!catTitle.trim() || catLoading"
          class="btn-primary w-full"
        >
          <svg v-if="catLoading" class="w-5 h-5 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          分析分类
        </button>

        <Transition name="fade">
          <div v-if="catResult" class="p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-xl space-y-3">
            <div class="flex items-center gap-3">
              <span class="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 font-medium">
                {{ categoryLabels[catResult.category] || catResult.category }}
              </span>
              <div class="flex gap-1">
                <span 
                  v-for="sub in catResult.subcategories" 
                  :key="sub"
                  class="px-2 py-0.5 rounded text-xs bg-dark-700 text-dark-300"
                >
                  {{ sub }}
                </span>
              </div>
            </div>
            <p class="text-sm text-dark-400">{{ catResult.reasoning }}</p>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Task Insights -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-display font-bold text-dark-100">任务洞察</h2>
            <p class="text-sm text-dark-400">AI 分析你的任务数据并提供建议</p>
          </div>
        </div>
        <button @click="loadInsights" :disabled="insightsLoading" class="btn-ghost text-sm">
          <svg v-if="insightsLoading" class="w-4 h-4 animate-spin mr-1" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          刷新
        </button>
      </div>

      <div v-if="insights" class="space-y-6">
        <!-- Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="p-4 rounded-xl bg-dark-800/50 text-center">
            <div class="text-2xl font-bold text-dark-100">{{ insights.total }}</div>
            <div class="text-xs text-dark-500">总任务数</div>
          </div>
          <div class="p-4 rounded-xl bg-dark-800/50 text-center">
            <div class="text-2xl font-bold text-emerald-400">{{ insights.completion_rate.toFixed(0) }}%</div>
            <div class="text-xs text-dark-500">完成率</div>
          </div>
          <div class="p-4 rounded-xl bg-dark-800/50 text-center">
            <div class="text-2xl font-bold text-amber-400">{{ insights.by_status?.in_progress || 0 }}</div>
            <div class="text-xs text-dark-500">进行中</div>
          </div>
          <div class="p-4 rounded-xl bg-dark-800/50 text-center">
            <div class="text-2xl font-bold text-red-400">{{ insights.by_priority?.high || 0 }}</div>
            <div class="text-xs text-dark-500">高优先级</div>
          </div>
        </div>

        <!-- Status Distribution -->
        <div class="space-y-2">
          <div class="text-sm font-medium text-dark-300">状态分布</div>
          <div class="flex gap-2 h-3 rounded-full overflow-hidden bg-dark-800">
            <div 
              v-if="insights.by_status?.completed"
              class="bg-emerald-500"
              :style="{ width: `${(insights.by_status.completed / insights.total) * 100}%` }"
            ></div>
            <div 
              v-if="insights.by_status?.in_progress"
              class="bg-amber-500"
              :style="{ width: `${(insights.by_status.in_progress / insights.total) * 100}%` }"
            ></div>
            <div 
              v-if="insights.by_status?.pending"
              class="bg-dark-600"
              :style="{ width: `${(insights.by_status.pending / insights.total) * 100}%` }"
            ></div>
          </div>
          <div class="flex gap-4 text-xs text-dark-500">
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              已完成 ({{ insights.by_status?.completed || 0 }})
            </span>
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-amber-500"></span>
              进行中 ({{ insights.by_status?.in_progress || 0 }})
            </span>
            <span class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-dark-600"></span>
              待处理 ({{ insights.by_status?.pending || 0 }})
            </span>
          </div>
        </div>

        <!-- AI Insights -->
        <div v-if="insights.insights.length" class="space-y-2">
          <div class="text-sm font-medium text-dark-300">AI 洞察</div>
          <ul class="space-y-2">
            <li 
              v-for="(insight, i) in insights.insights" 
              :key="i"
              class="flex items-start gap-2 text-sm text-dark-400"
            >
              <svg class="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ insight }}
            </li>
          </ul>
        </div>

        <!-- Recommendations -->
        <div v-if="insights.recommendations.length" class="space-y-2">
          <div class="text-sm font-medium text-dark-300">建议</div>
          <ul class="space-y-2">
            <li 
              v-for="(rec, i) in insights.recommendations" 
              :key="i"
              class="flex items-start gap-2 text-sm text-dark-400"
            >
              <svg class="w-4 h-4 text-primary-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ rec }}
            </li>
          </ul>
        </div>
      </div>

      <div v-else class="text-center py-8 text-dark-500">
        <svg v-if="insightsLoading" class="w-8 h-8 animate-spin mx-auto mb-2" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <p v-else>暂无数据</p>
      </div>
    </div>

    <!-- AI Tips -->
    <div class="card p-6 bg-gradient-to-br from-accent-500/5 to-primary-500/5 border-accent-500/20">
      <h3 class="font-display font-bold text-dark-200 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        AI 功能提示
      </h3>
      <ul class="space-y-2 text-sm text-dark-400">
        <li class="flex items-start gap-2">
          <span class="text-primary-400">•</span>
          <span>使用"紧急"、"重要"等词语会自动设置高优先级</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-primary-400">•</span>
          <span>在任务列表中点击展开可使用 AI 任务分解功能</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-primary-400">•</span>
          <span>语义搜索可以找到含义相近但关键词不同的任务</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-primary-400">•</span>
          <span>智能分类帮助你自动整理和归类任务</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-primary-400">•</span>
          <span>支持中英文混合输入</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

