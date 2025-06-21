<template>
  <div class="card">
    <div class="flex items-center mb-4">
      <h2 class="text-lg font-semibold text-gray-900">智能选题</h2>
      <div class="ml-auto space-x-2">
        <button 
          @click="refreshTopics"
          :disabled="loading"
          class="btn-secondary text-sm"
        >
          {{ loading ? '生成中...' : '刷新选题' }}
        </button>
        <button 
          @click="showWeChatModal = true"
          class="btn-primary text-sm"
        >
          微信分析
        </button>
      </div>
    </div>

    <!-- 微信文章分析Modal -->
    <div v-if="showWeChatModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96 max-w-lg">
        <h3 class="text-lg font-semibold mb-4">微信公众号文章分析</h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            文章链接（支持多个，每行一个）
          </label>
          <textarea 
            v-model="wechatUrls"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://mp.weixin.qq.com/s/..."
          ></textarea>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            生成选题数量
          </label>
          <select v-model="wechatLimit" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="5">5个</option>
            <option value="10">10个</option>
            <option value="15">15个</option>
          </select>
        </div>
        
        <div class="flex space-x-3">
          <button 
            @click="analyzeWeChatArticles"
            :disabled="wechatAnalyzing"
            class="btn-primary flex-1"
          >
            {{ wechatAnalyzing ? '分析中...' : '开始分析' }}
          </button>
          <button 
            @click="showWeChatModal = false"
            class="btn-secondary flex-1"
          >
            取消
          </button>
        </div>
      </div>
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

// 微信分析相关状态
const showWeChatModal = ref(false)
const wechatUrls = ref('https://mp.weixin.qq.com/s/LZgG-5uE8fGaJAiqb0FGYQ')
const wechatLimit = ref(5)
const wechatAnalyzing = ref(false)

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

// 微信文章分析功能
const analyzeWeChatArticles = async () => {
  if (!wechatUrls.value.trim()) {
    alert('请输入微信文章链接')
    return
  }

  wechatAnalyzing.value = true
  
  try {
    // 解析URL列表
    const urls = wechatUrls.value
      .split('\n')
      .map(url => url.trim())
      .filter(url => url && url.includes('mp.weixin.qq.com'))

    if (urls.length === 0) {
      alert('请输入有效的微信公众号文章链接')
      return
    }

    // 调用后端API
    const response = await fetch('/api/topics/trending/wechat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        urls: urls,
        limit: parseInt(wechatLimit.value)
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    
    // 更新选题列表
    topics.value = data
    showWeChatModal.value = false
    
    // 显示成功消息
    alert(`成功分析 ${urls.length} 篇文章，生成 ${data.length} 个选题！`)
    
  } catch (error) {
    console.error('微信文章分析失败:', error)
    
    // 如果API失败，使用演示数据
    try {
      const demoResponse = await fetch('/api/topics/demo/wechat')
      const demoData = await demoResponse.json()
      
      if (demoData.generated_topics) {
        topics.value = demoData.generated_topics
        alert('演示模式：已生成示例选题（实际爬取可能受限）')
      } else {
        throw new Error('演示数据获取失败')
      }
    } catch (demoError) {
      alert('分析失败，请检查网络连接或稍后重试')
    }
  } finally {
    wechatAnalyzing.value = false
  }
}

onMounted(() => {
  refreshTopics()
})
</script>