<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">副业有道内容引擎</h1>
            <span class="ml-2 text-sm text-gray-500">MVP</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Topic Finder -->
        <div class="lg:col-span-1">
          <TopicFinder @topic-selected="handleTopicSelected" />
        </div>
        
        <!-- Content Generator -->
        <div class="lg:col-span-2">
          <ContentGenerator :selected-topic="selectedTopic" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopicFinder from './components/TopicFinder.vue'
import ContentGenerator from './components/ContentGenerator.vue'

const selectedTopic = ref(null)

const handleTopicSelected = (topic) => {
  selectedTopic.value = topic
}
</script>