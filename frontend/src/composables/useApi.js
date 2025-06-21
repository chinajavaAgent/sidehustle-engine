import { ref } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const apiCall = async (url, options = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 选题相关API
  const getTopics = () => apiCall('/topics/trending')
  const searchTopics = (keyword) => apiCall(`/topics/search?keyword=${encodeURIComponent(keyword)}`)
  const getCategories = () => apiCall('/topics/categories')

  // 内容生成相关API
  const generateContent = (data) => apiCall('/content/generate', {
    method: 'POST',
    body: JSON.stringify(data)
  })
  
  const getFrameworks = () => apiCall('/content/frameworks')
  
  const optimizeTitle = (title) => apiCall('/content/optimize/title', {
    method: 'POST',
    body: JSON.stringify({ title })
  })

  return {
    loading,
    error,
    getTopics,
    searchTopics,
    getCategories,
    generateContent,
    getFrameworks,
    optimizeTitle
  }
}