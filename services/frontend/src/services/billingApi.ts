import api from './api'

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
    const response = await api.get('/billing/api/plans/')
    return response.data.results
  }

  async getCurrentSubscription(): Promise<UserSubscription> {
    const response = await api.get('/billing/api/subscriptions/me/')
    return response.data
  }

  async changePlan(subscriptionId: number, planId: number, reason?: string): Promise<UserSubscription> {
    const response = await api.post(`/billing/api/subscriptions/${subscriptionId}/change_plan/`, {
      plan_id: planId,
      reason
    })
    return response.data
  }

  async cancelSubscription(subscriptionId: number, reason?: string): Promise<UserSubscription> {
    const response = await api.post(`/billing/api/subscriptions/${subscriptionId}/cancel/`, {
      reason
    })
    return response.data
  }

  async getInvoices(): Promise<Invoice[]> {
    const response = await api.get('/billing/api/invoices/')
    return response.data.results
  }

  async getUsageSummary(): Promise<ApiUsageSummary> {
    const response = await api.get('/billing/api/usage-logs/summary/')
    return response.data
  }

  async getBillingStats(): Promise<BillingStats> {
    const response = await api.get('/billing/api/stats/dashboard/')
    return response.data
  }

  async createSubscription(planId: number, billingCycle: 'monthly' | 'yearly'): Promise<UserSubscription> {
    const response = await api.post('/billing/api/subscriptions/', {
      plan_id: planId,
      billing_cycle: billingCycle
    })
    return response.data
  }
}

export const billingApi = new BillingApiService()
