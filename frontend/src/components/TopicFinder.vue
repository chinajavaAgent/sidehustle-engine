<template>
  <div class="card">
    <div class="flex items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-900">智能选题</h2>
      <button 
        @click="refreshTopics"
        :disabled="loading"
        class="ml-auto btn-secondary text-sm"
      >
        {{ loading ? '生成中...' : '刷新选题' }}
      </button>
    </div>

    <!-- Topic List -->
    <div class="space-y-3">
      <div 
        v-for="topic in topics" 
        :key="topic.id"
        class="p-3 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors"
        :class="{ 'border-blue-500 bg-blue-50': selectedTopicId === topic.id }"
        @click="selectTopic(topic)"
      >
        <h3 class="font-medium text-gray-900 mb-1">{{ topic.title }}</h3>
        <p class="text-sm text-gray-600 mb-2">{{ topic.reason }}</p>
        <div class="flex items-center space-x-2 text-xs">
          <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded">{{ topic.category }}</span>
          <span class="text-gray-500">热度: {{ topic.heat }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!topics.length && !loading" class="text-center py-8 text-gray-500">
      <p>暂无选题推荐</p>
      <button @click="refreshTopics" class="btn-primary mt-2">生成选题</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['topic-selected'])

const topics = ref([])
const loading = ref(false)
const selectedTopicId = ref(null)

const mockTopics = [
  {
    id: 1,
    title: 'AI绘画接单，月入过万的新兴副业',
    reason: '近期AI绘画工具火爆，市场需求大',
    category: 'AI工具',
    heat: 85
  },
  {
    id: 2,
    title: '闲鱼卖货实战指南：从0到月收入5000+',
    reason: '电商副业门槛低，适合新手入门',
    category: '电商变现',
    heat: 78
  },
  {
    id: 3,
    title: '短视频剪辑接私活，学生党也能月入3000',
    reason: '短视频内容需求旺盛，技能门槛适中',
    category: '内容创作',
    heat: 72
  }
]

const refreshTopics = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    topics.value = [...mockTopics]
  } catch (error) {
    console.error('获取选题失败:', error)
  } finally {
    loading.value = false
  }
}

const selectTopic = (topic) => {
  selectedTopicId.value = topic.id
  emit('topic-selected', topic)
}

onMounted(() => {
  refreshTopics()
})
</script>