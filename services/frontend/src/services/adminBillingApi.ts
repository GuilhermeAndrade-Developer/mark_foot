import api from './api'

// Override base URL for admin billing API calls  
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1'
const ADMIN_BILLING_BASE_URL = API_BASE_URL.replace('/api/v1', '/api/billing/admin')

// Helper function to make admin billing API calls
const adminBillingRequest = async (endpoint: string, options: any = {}) => {
  const originalBaseURL = api.defaults.baseURL
  api.defaults.baseURL = ADMIN_BILLING_BASE_URL
  
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

export interface AdminKPIs {
  mrr: number
  mrr_growth: number
  active_subscribers: number
  subscriber_growth: number
  churn_rate: number
  churn_trend: number
  arpu: number
  arpu_growth: number
}

export interface RevenueChartData {
  chart: {
    labels: string[]
    datasets: Array<{
      label: string
      data: number[]
      borderColor: string
      backgroundColor: string
    }>
  }
  plans_stats: Array<{
    name: string
    count: number
    percentage: number
    revenue: number
  }>
  plans_chart: {
    labels: string[]
    datasets: Array<{
      data: number[]
      backgroundColor: string[]
    }>
  }
}

export interface AdminSubscription {
  id: number
  user: {
    id: number
    full_name: string
    email: string
    avatar?: string
    created_at: string
    last_login?: string
  }
  plan: {
    id: number
    name: string
    plan_type: string
    price_monthly: number
    price_yearly: number
    api_calls_limit: number
  }
  status: string
  billing_cycle: string
  started_at: string
  expires_at: string
  cancelled_at?: string
  api_calls_used: number
  api_usage_percentage: number
  total_revenue: number
  last_payment?: string
}

export interface PaymentIntegrations {
  stripe: {
    connected: boolean
    webhook_url?: string
    webhooks_count: number
    last_sync?: string
    transactions_today: number
    test_mode: boolean
    account_id?: string
  }
  pagseguro: {
    connected: boolean
    environment: 'sandbox' | 'production'
    last_sync?: string
    transactions_today: number
    account_id?: string
  }
}

export interface ConversionMetrics {
  lead_to_trial: number
  trial_to_paid: number
  average_ltv: number
  customer_acquisition_cost: number
  payback_period: number
}

export interface APIMetrics {
  calls_today: number
  calls_month: number
  calls_year: number
  daily_limit: number
  monthly_limit: number
  top_endpoint: string
  endpoints_usage: Array<{
    endpoint: string
    count: number
    percentage: number
  }>
  error_rate: number
  avg_response_time: number
}

export interface SystemAlert {
  id: string
  type: 'success' | 'info' | 'warning' | 'error'
  message: string
  action?: string
  created_at: string
}

export interface CustomerDetails {
  id: number
  full_name: string
  email: string
  avatar?: string
  created_at: string
  last_login?: string
  subscription_history: Array<{
    plan_name: string
    started_at: string
    ended_at?: string
    revenue: number
  }>
  payment_history: Array<{
    id: number
    amount: number
    status: string
    method: string
    created_at: string
  }>
  api_usage_history: Array<{
    date: string
    calls: number
    limit: number
  }>
  support_tickets: number
  lifetime_value: number
}

class AdminBillingApiService {
  async getKPIs(): Promise<AdminKPIs> {
    const response = await adminBillingRequest('/kpis/', { method: 'GET' })
    return response.data
  }

  async getRevenueChart(timeframe: string = '30d'): Promise<RevenueChartData> {
    const response = await adminBillingRequest(`/revenue-chart/?timeframe=${timeframe}`, { method: 'GET' })
    return response.data
  }

  async getSubscriptions(page: number = 1, search?: string): Promise<{
    results: AdminSubscription[]
    count: number
    next?: string
    previous?: string
  }> {
    let url = `/subscriptions/?page=${page}`
    if (search) {
      url += `&search=${encodeURIComponent(search)}`
    }
    
    const response = await adminBillingRequest(url, { method: 'GET' })
    return response.data
  }

  async getCustomerDetails(userId: number): Promise<CustomerDetails> {
    const response = await adminBillingRequest(`/customers/${userId}/`, { method: 'GET' })
    return response.data
  }

  async updateSubscription(subscriptionId: number, data: {
    plan_id?: number
    status?: string
    expires_at?: string
    billing_cycle?: string
    auto_renewal?: boolean
  }): Promise<AdminSubscription> {
    const response = await adminBillingRequest(`/subscriptions/${subscriptionId}/`, {
      method: 'PATCH',
      data
    })
    return response.data
  }

  async cancelSubscription(subscriptionId: number, reason: string): Promise<AdminSubscription> {
    const response = await adminBillingRequest(`/subscriptions/${subscriptionId}/cancel/`, {
      method: 'POST',
      data: { reason, admin_action: true }
    })
    return response.data
  }

  async createSubscription(data: {
    user_id: number
    plan_id: number
    billing_cycle: 'monthly' | 'yearly'
    starts_immediately?: boolean
  }): Promise<AdminSubscription> {
    const response = await adminBillingRequest('/subscriptions/', {
      method: 'POST',
      data
    })
    return response.data
  }

  async getPaymentIntegrations(): Promise<PaymentIntegrations> {
    const response = await adminBillingRequest('/integrations/', { method: 'GET' })
    return response.data
  }

  async connectStripe(data: {
    publishable_key: string
    secret_key: string
    webhook_secret: string
    test_mode?: boolean
  }): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/stripe/connect/', {
      method: 'POST',
      data
    })
    return response.data
  }

  async disconnectStripe(): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/stripe/disconnect/', {
      method: 'POST'
    })
    return response.data
  }

  async connectPagSeguro(data: {
    email: string
    token: string
    environment: 'sandbox' | 'production'
  }): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/pagseguro/connect/', {
      method: 'POST',
      data
    })
    return response.data
  }

  async disconnectPagSeguro(): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/pagseguro/disconnect/', {
      method: 'POST'
    })
    return response.data
  }

  async testStripeConnection(): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/stripe/test/', {
      method: 'POST'
    })
    return response.data
  }

  async testPagSeguroConnection(): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest('/integrations/pagseguro/test/', {
      method: 'POST'
    })
    return response.data
  }

  async getMetrics(): Promise<{
    conversion: ConversionMetrics
    api: APIMetrics
  }> {
    const response = await adminBillingRequest('/metrics/', { method: 'GET' })
    return response.data
  }

  async getSystemAlerts(): Promise<{ alerts: SystemAlert[] }> {
    const response = await adminBillingRequest('/alerts/', { method: 'GET' })
    return response.data
  }

  async dismissAlert(alertId: string): Promise<{ success: boolean }> {
    const response = await adminBillingRequest(`/alerts/${alertId}/dismiss/`, {
      method: 'POST'
    })
    return response.data
  }

  async exportReport(timeframe: string = '30d', format: 'xlsx' | 'csv' = 'xlsx'): Promise<Blob> {
    const response = await adminBillingRequest(`/export/?timeframe=${timeframe}&format=${format}`, {
      method: 'GET',
      responseType: 'blob'
    })
    return response.data
  }

  async sendCustomerEmail(userId: number, data: {
    subject: string
    message: string
    template?: string
  }): Promise<{ success: boolean; message: string }> {
    const response = await adminBillingRequest(`/customers/${userId}/send-email/`, {
      method: 'POST',
      data
    })
    return response.data
  }

  async refundPayment(paymentId: number, data: {
    amount?: number
    reason: string
    full_refund?: boolean
  }): Promise<{ success: boolean; message: string; refund_id?: string }> {
    const response = await adminBillingRequest(`/payments/${paymentId}/refund/`, {
      method: 'POST',
      data
    })
    return response.data
  }

  async getFinancialSummary(timeframe: string = '30d'): Promise<{
    total_revenue: number
    total_refunds: number
    net_revenue: number
    new_subscriptions: number
    cancelled_subscriptions: number
    upgrade_revenue: number
    churn_revenue: number
    payment_methods_distribution: Record<string, number>
  }> {
    const response = await adminBillingRequest(`/financial-summary/?timeframe=${timeframe}`, {
      method: 'GET'
    })
    return response.data
  }

  async getRevenueProjection(months: number = 12): Promise<{
    projected_revenue: Array<{
      month: string
      projected_mrr: number
      projected_arr: number
      confidence: number
    }>
    growth_scenarios: {
      conservative: number
      realistic: number
      optimistic: number
    }
  }> {
    const response = await adminBillingRequest(`/revenue-projection/?months=${months}`, {
      method: 'GET'
    })
    return response.data
  }

  async getCohortAnalysis(timeframe: string = '12m'): Promise<{
    cohorts: Array<{
      cohort_month: string
      users_count: number
      retention_rates: number[]
      revenue_rates: number[]
    }>
    overall_retention: number[]
  }> {
    const response = await adminBillingRequest(`/cohort-analysis/?timeframe=${timeframe}`, {
      method: 'GET'
    })
    return response.data
  }

  // Dashboard specific methods
  async getDashboardKpis(): Promise<AdminKPIs> {
    try {
      const response = await adminBillingRequest('/dashboard/kpis/', { method: 'GET' })
      return response.data
    } catch (error) {
      console.warn('Dashboard KPIs API not available, using mock data')
      throw error
    }
  }

  async getPlanDistribution(): Promise<{ free: number; premium: number; enterprise: number }> {
    try {
      const response = await adminBillingRequest('/dashboard/plan-distribution/', { method: 'GET' })
      return response.data
    } catch (error) {
      console.warn('Plan distribution API not available, using mock data')
      throw error
    }
  }

  async getRecentTransactions(): Promise<Array<{
    id: number
    customer: { name: string; email: string }
    amount: number
    status: string
    date: string
    plan: string
  }>> {
    try {
      const response = await adminBillingRequest('/dashboard/recent-transactions/', { method: 'GET' })
      return response.data
    } catch (error) {
      console.warn('Recent transactions API not available, using mock data')
      throw error
    }
  }

  async getIntegrationStatus(): Promise<{
    stripe: { status: string }
    pagseguro: { status: string }
  }> {
    try {
      const response = await adminBillingRequest('/dashboard/integration-status/', { method: 'GET' })
      return response.data
    } catch (error) {
      console.warn('Integration status API not available, using mock data')
      throw error
    }
  }

  async getCustomers(): Promise<{ data: Array<{ id: number; first_name: string; last_name: string; email: string }> }> {
    try {
      const response = await adminBillingRequest('/customers/', { method: 'GET' })
      return response
    } catch (error) {
      console.warn('Customers API not available, using mock data')
      throw error
    }
  }

  async getPlans(): Promise<{ data: Array<{ id: number; name: string; price_monthly: number }> }> {
    try {
      const response = await adminBillingRequest('/plans/', { method: 'GET' })
      return response
    } catch (error) {
      console.warn('Plans API not available, using mock data')
      throw error
    }
  }

  async createInvoice(data: {
    customer_id: number
    plan_id: number
    amount: number
    description: string
  }): Promise<{ success: boolean; invoice_id?: number; message: string }> {
    try {
      const response = await adminBillingRequest('/invoices/', {
        method: 'POST',
        data
      })
      return response.data
    } catch (error) {
      console.warn('Create invoice API not available')
      throw error
    }
  }
}

export const adminBillingApi = new AdminBillingApiService()
