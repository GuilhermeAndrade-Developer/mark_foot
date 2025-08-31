import api from './api'

// Override base URL for billing API calls  
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1'
const BILLING_BASE_URL = API_BASE_URL.replace('/api/v1', '/api/billing/api')

// Helper function to make billing API calls
const billingRequest = async (endpoint: string, options: any = {}) => {
  const originalBaseURL = api.defaults.baseURL
  api.defaults.baseURL = BILLING_BASE_URL
  
  try {
    const response = await api.request({
      url: endpoint,
      ...options
    })
    return response
  } finally {
    api.defaults.baseURL = originalBaseURL
  }
}

export interface SubscriptionPlan {
  id: number
  name: string
  plan_type: string
  description: string
  price_monthly: number
  price_yearly: number
  api_calls_limit: number
  advanced_ai_analysis: boolean
  unlimited_reports: boolean
  white_label: boolean
  dedicated_support: boolean
  multi_tenancy: boolean
  features: Record<string, any>
  is_active: boolean
}

export interface UserSubscription {
  id: number
  plan: SubscriptionPlan
  status: string
  billing_cycle: string
  started_at: string
  expires_at: string
  cancelled_at?: string
  api_calls_used: number
  api_calls_reset_date: string
  auto_renewal: boolean
  days_remaining: number
  api_calls_remaining: number
  api_usage_percentage: number
  is_expired: boolean
}

export interface Invoice {
  id: number
  invoice_number: string
  subscription_plan: string
  subtotal: number
  tax_amount: number
  discount_amount: number
  total_amount: number
  currency: string
  status: string
  issue_date: string
  due_date: string
  paid_at?: string
  billing_period_start: string
  billing_period_end: string
}

export interface ApiUsageSummary {
  monthly_usage: number
  limit: number
  remaining: number
  percentage: number
  usage_by_endpoint: Array<{
    endpoint: string
    count: number
  }>
}

export interface BillingStats {
  total_users: number
  active_subscriptions: number
  plan_distribution: Record<string, number>
  monthly_revenue: number
  api_usage_stats: {
    total_calls_today: number
    total_calls_month: number
    top_endpoints: Array<{
      endpoint: string
      count: number
    }>
  }
}

class BillingApiService {
  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await billingRequest('/plans/', { method: 'GET' })
    return response.data.results
  }

  async getCurrentSubscription(): Promise<UserSubscription> {
    const response = await billingRequest('/subscriptions/me/', { method: 'GET' })
    return response.data
  }

  async changePlan(subscriptionId: number, planId: number, reason?: string): Promise<UserSubscription> {
    const response = await billingRequest(`/subscriptions/${subscriptionId}/change_plan/`, {
      method: 'POST',
      data: {
        plan_id: planId,
        reason
      }
    })
    return response.data
  }

  async cancelSubscription(subscriptionId: number, reason?: string): Promise<UserSubscription> {
    const response = await billingRequest(`/subscriptions/${subscriptionId}/cancel/`, {
      method: 'POST',
      data: { reason }
    })
    return response.data
  }

  async getInvoices(): Promise<Invoice[]> {
    const response = await billingRequest('/invoices/', { method: 'GET' })
    return response.data.results
  }

  async getUsageSummary(): Promise<ApiUsageSummary> {
    const response = await billingRequest('/usage-logs/summary/', { method: 'GET' })
    return response.data
  }

  async getBillingStats(): Promise<BillingStats> {
    const response = await billingRequest('/stats/dashboard/', { method: 'GET' })
    return response.data
  }

  async createSubscription(planId: number, billingCycle: 'monthly' | 'yearly'): Promise<UserSubscription> {
    const response = await billingRequest('/subscriptions/', {
      method: 'POST',
      data: {
        plan_id: planId,
        billing_cycle: billingCycle
      }
    })
    return response.data
  }
}

export const billingApi = new BillingApiService()
