<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useTaskStore } from '../stores/tasks'
import type { TaskCreate, TaskPriority, TaskStatus } from '../types/task'

const props = defineProps<{
  taskId?: number | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const store = useTaskStore()

const form = ref<TaskCreate>({
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  tags: []
})

const tagInput = ref('')
const loading = ref(false)
const isEditing = computed(() => !!props.taskId)

const priorities: { value: TaskPriority; label: string; color: string }[] = [
  { value: 'low', label: '低', color: 'text-green-400' },
  { value: 'medium', label: '中', color: 'text-yellow-400' },
  { value: 'high', label: '高', color: 'text-red-400' }
]

const statuses: { value: TaskStatus; label: string }[] = [
  { value: 'pending', label: '待处理' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' }
]

onMounted(async () => {
  if (props.taskId) {
    await store.fetchTask(props.taskId)
    if (store.currentTask) {
      form.value = {
        title: store.currentTask.title,
        description: store.currentTask.description || '',
        status: store.currentTask.status,
        priority: store.currentTask.priority,
        tags: [...store.currentTask.tags]
      }
    }
  }
})

function addTag() {
  const tag = tagInput.value.trim().toLowerCase()
  if (tag && !form.value.tags?.includes(tag)) {
    form.value.tags = [...(form.value.tags || []), tag]
  }
  tagInput.value = ''
}

function removeTag(tag: string) {
  form.value.tags = form.value.tags?.filter(t => t !== tag) || []
}

async function handleSubmit() {
  if (!form.value.title.trim()) return
  
  loading.value = true
  try {
    if (isEditing.value && props.taskId) {
      await store.updateTask(props.taskId, form.value)
    } else {
      await store.createTask(form.value)
    }
    emit('saved')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-display font-bold text-gradient">
        {{ isEditing ? '编辑任务' : '新建任务' }}
      </h2>
      <button 
        type="button" 
        @click="emit('close')"
        class="p-2 rounded-lg hover:bg-dark-800 text-dark-400 hover:text-dark-200 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="space-y-5">
      <!-- Title -->
      <div>
        <label class="label">任务标题 <span class="text-red-400">*</span></label>
        <input 
          v-model="form.title"
          type="text"
          class="input"
          placeholder="输入任务标题..."
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label class="label">描述</label>
        <textarea 
          v-model="form.description"
          class="input min-h-[100px] resize-none"
          placeholder="添加详细描述..."
          rows="3"
        ></textarea>
      </div>

      <!-- Priority & Status -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">优先级</label>
          <div class="flex gap-2">
            <button 
              v-for="p in priorities"
              :key="p.value"
              type="button"
              @click="form.priority = p.value"
              :class="[
                'flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all border',
                form.priority === p.value 
                  ? `priority-${p.value}` 
                  : 'bg-dark-800/50 border-dark-700 text-dark-400 hover:bg-dark-800'
              ]"
            >
              {{ p.label }}
            </button>
          </div>
        </div>

        <div>
          <label class="label">状态</label>
          <select v-model="form.status" class="input">
            <option v-for="s in statuses" :key="s.value" :value="s.value">
              {{ s.label }}
            </option>
          </select>
        </div>
      </div>

      <!-- Tags -->
      <div>
        <label class="label">标签</label>
        <div class="flex gap-2 mb-2">
          <input 
            v-model="tagInput"
            type="text"
            class="input flex-1"
            placeholder="添加标签..."
            @keydown.enter.prevent="addTag"
          />
          <button 
            type="button"
            @click="addTag"
            class="btn-ghost px-4"
          >
            添加
          </button>
        </div>
        <div v-if="form.tags?.length" class="flex flex-wrap gap-2">
          <span 
            v-for="tag in form.tags" 
            :key="tag"
            class="tag-primary flex items-center gap-1"
          >
            {{ tag }}
            <button 
              type="button"
              @click="removeTag(tag)"
              class="hover:text-primary-200 transition-colors"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3 mt-8 pt-6 border-t border-dark-800">
      <button 
        type="button"
        @click="emit('close')"
        class="btn-ghost"
      >
        取消
      </button>
      <button 
        type="submit"
        :disabled="loading || !form.title.trim()"
        class="btn-primary min-w-[100px]"
      >
        <span v-if="loading" class="flex items-center gap-2">
          <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          保存中...
        </span>
        <span v-else>{{ isEditing ? '保存' : '创建' }}</span>
      </button>
    </div>
  </form>
</template>

