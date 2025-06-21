<template>
  <div class="space-y-6">
    <!-- Article Framework Selection -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">文章框架</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div 
          v-for="framework in frameworks"
          :key="framework.id"
          class="p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 transition-colors"
          :class="{ 'border-blue-500 bg-blue-50': selectedFramework?.id === framework.id }"
          @click="selectedFramework = framework"
        >
          <h3 class="font-medium text-gray-900">{{ framework.name }}</h3>
          <p class="text-sm text-gray-600 mt-1">{{ framework.description }}</p>
        </div>
      </div>
    </div>

    <!-- Content Generation -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900">内容生成</h2>
        <button 
          @click="generateContent"
          :disabled="!selectedTopic || !selectedFramework || generating"
          class="btn-primary"
        >
          {{ generating ? '生成中...' : '生成文章' }}
        </button>
      </div>

      <!-- Topic Display -->
      <div v-if="selectedTopic" class="mb-4 p-3 bg-gray-50 rounded-lg">
        <h3 class="font-medium text-gray-900">选定主题:</h3>
        <p class="text-gray-700">{{ selectedTopic.title }}</p>
      </div>

      <!-- Generated Content -->
      <div v-if="generatedContent" class="space-y-4">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">标题</label>
          <input 
            v-model="generatedContent.title" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Content -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">正文内容</label>
          <textarea 
            v-model="generatedContent.content" 
            rows="15"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>

        <!-- Actions -->
        <div class="flex space-x-3">
          <button @click="optimizeTitle" class="btn-secondary">优化标题</button>
          <button @click="polishContent" class="btn-secondary">润色内容</button>
          <button @click="formatContent" class="btn-primary">格式化排版</button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!generating" class="text-center py-8 text-gray-500">
        <p>请选择主题和框架后生成文章</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  selectedTopic: Object
})

const frameworks = ref([
  {
    id: 1,
    name: '痛点+解决方案型',
    description: '分析问题痛点，提供解决方案'
  },
  {
    id: 2,
    name: '故事+干货型',
    description: '真实案例故事，配合实用干货'
  },
  {
    id: 3,
    name: '教程+步骤型',
    description: '详细操作教程，分步骤指导'
  },
  {
    id: 4,
    name: '盘点+评测型',
    description: '多个选项对比，客观评测分析'
  }
])

const selectedFramework = ref(null)
const generating = ref(false)
const generatedContent = ref(null)

const generateContent = async () => {
  if (!props.selectedTopic || !selectedFramework.value) return
  
  generating.value = true
  try {
    // 模拟AI生成内容
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    generatedContent.value = {
      title: generateTitle(),
      content: generateArticleContent()
    }
  } catch (error) {
    console.error('生成内容失败:', error)
  } finally {
    generating.value = false
  }
}

const generateTitle = () => {
  const titles = [
    `${props.selectedTopic.title}：真实案例分享`,
    `揭秘${props.selectedTopic.title.split('：')[0]}，普通人也能做到`,
    `${props.selectedTopic.title}完全指南，新手必看`,
    `我靠${props.selectedTopic.title.split('：')[0]}月入过万的全过程`
  ]
  return titles[Math.floor(Math.random() * titles.length)]
}

const generateArticleContent = () => {
  return `## 前言

大家好，我是小王。最近很多朋友问我关于${props.selectedTopic.title.split('：')[0]}的问题，今天就来详细分享一下我的经验。

## 为什么选择这个副业

${props.selectedTopic.reason}，而且门槛相对较低，适合大部分人尝试。

## 具体操作步骤

### 第一步：准备工作
- 了解市场需求
- 准备必要工具
- 学习基础技能

### 第二步：实践操作
- 制作作品集
- 寻找客户渠道
- 建立服务流程

### 第三步：优化提升
- 提高作品质量
- 扩大客户群体
- 建立口碑品牌

## 收入情况

根据我的实际经验，新手第一个月可能收入在500-1000元，熟练后月收入3000-8000元是比较常见的。

## 注意事项

1. 保持耐心，前期可能收入较少
2. 不断学习提升专业技能
3. 建立良好的客户关系

## 总结

${props.selectedTopic.title.split('：')[0]}确实是一个不错的副业选择，但需要付出时间和精力去学习和实践。希望这份分享对大家有帮助！

如果你也想开始这个副业，欢迎在评论区留言交流，我会尽量回复大家的问题。

---

*关注我，了解更多副业赚钱方法！*`
}

const optimizeTitle = () => {
  // 模拟标题优化
  alert('标题优化功能开发中...')
}

const polishContent = () => {
  // 模拟内容润色
  alert('内容润色功能开发中...')
}

const formatContent = () => {
  // 模拟格式化
  alert('格式化排版功能开发中...')
}
</script>