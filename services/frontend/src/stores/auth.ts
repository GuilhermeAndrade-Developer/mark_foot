import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService } from '@/services/api'

interface User {
  id: number
  username: string
  email?: string
  first_name?: string
  last_name?: string
  is_staff?: boolean
  is_superuser?: boolean
}

interface LoginCredentials {
  username: string
  password: string
  rememberMe?: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const lastActivity = ref<Date | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_staff || user.value?.is_superuser || false)
  const fullName = computed(() => {
    if (!user.value) return ''
    const { first_name, last_name, username } = user.value
    if (first_name && last_name) {
      return `${first_name} ${last_name}`
    }
    return username
  })

  // Actions
  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      isLoading.value = true
      
      // For now, simulate login with hardcoded credentials
      // In production, this would call the actual API
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        // Simulate API response
        const response = {
          access: 'fake-jwt-token-' + Date.now(),
          refresh: 'fake-refresh-token-' + Date.now(),
          user: {
            id: 1,
            username: 'admin',
            email: 'admin@markfoot.com',
            first_name: 'Admin',
            last_name: 'User',
            is_staff: true,
            is_superuser: true
          }
        }
        
        // Store tokens and user data
        token.value = response.access
        refreshToken.value = response.refresh
        user.value = response.user
        lastActivity.value = new Date()
        
        // Store in localStorage if remember me is checked
        if (credentials.rememberMe) {
          localStorage.setItem('auth_token', response.access)
          localStorage.setItem('refresh_token', response.refresh)
          localStorage.setItem('user_data', JSON.stringify(response.user))
        } else {
          sessionStorage.setItem('auth_token', response.access)
          sessionStorage.setItem('refresh_token', response.refresh)
          sessionStorage.setItem('user_data', JSON.stringify(response.user))
        }
        
        // Configure API service with token
        ApiService.setAuthToken(response.access)
        
        return true
      } else {
        return false
      }
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      isLoading.value = true
      
      // Clear tokens and user data
      token.value = null
      refreshToken.value = null
      user.value = null
      lastActivity.value = null
      
      // Clear storage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('refresh_token')
      sessionStorage.removeItem('user_data')
      
      // Remove token from API service
      ApiService.removeAuthToken()
      
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      isLoading.value = false
    }
  }

  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      if (!refreshToken.value) {
        return false
      }
      
      // For now, simulate token refresh
      // In production, this would call the actual refresh endpoint
      const newToken = 'refreshed-jwt-token-' + Date.now()
      
      token.value = newToken
      lastActivity.value = new Date()
      
      // Update stored token
      const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage
      storage.setItem('auth_token', newToken)
      
      // Update API service token
      ApiService.setAuthToken(newToken)
      
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, logout user
      await logout()
      return false
    }
  }

  const initializeAuth = (): boolean => {
    try {
      // Check for stored auth data
      const storedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
      const storedRefreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
      const storedUserData = localStorage.getItem('user_data') || sessionStorage.getItem('user_data')
      
      if (storedToken && storedUserData) {
        token.value = storedToken
        refreshToken.value = storedRefreshToken
        user.value = JSON.parse(storedUserData)
        lastActivity.value = new Date()
        
        // Configure API service with token
        ApiService.setAuthToken(storedToken)
        
        return true
      }
      
      return false
    } catch (error) {
      console.error('Auth initialization error:', error)
      return false
    }
  }

  const updateActivity = (): void => {
    if (isAuthenticated.value) {
      lastActivity.value = new Date()
    }
  }

  const checkTokenExpiry = (): boolean => {
    if (!lastActivity.value) return false
    
    // Check if token might be expired (8 hours of inactivity)
    const now = new Date()
    const diffHours = (now.getTime() - lastActivity.value.getTime()) / (1000 * 60 * 60)
    
    return diffHours > 8
  }

  return {
    // State
    user,
    token,
    isLoading,
    lastActivity,
    
    // Getters
    isAuthenticated,
    isAdmin,
    fullName,
    
    // Actions
    login,
    logout,
    refreshAccessToken,
    initializeAuth,
    updateActivity,
    checkTokenExpiry
  }
})
