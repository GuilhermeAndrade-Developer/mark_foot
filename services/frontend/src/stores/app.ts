import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // State
  const loading = ref(false)
  const error = ref<string | null>(null)
  const theme = ref('light')
  
  // Getters
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const isDarkTheme = computed(() => theme.value === 'dark')
  
  // Actions
  const setLoading = (value: boolean) => {
    loading.value = value
  }
  
  const setError = (message: string | null) => {
    error.value = message
  }
  
  const clearError = () => {
    error.value = null
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  
  return {
    // State
    loading,
    error,
    theme,
    
    // Getters
    isLoading,
    hasError,
    isDarkTheme,
    
    // Actions
    setLoading,
    setError,
    clearError,
    toggleTheme
  }
})
