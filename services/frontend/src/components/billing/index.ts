// Billing module components
// export { default as FinanceiroDashboard } from './FinanceiroDashboard.vue'  // Moved to AdminFinanceiro view
export { default as PlansDialog } from './PlansDialog.vue'
export { default as InvoicesDialog } from './InvoicesDialog.vue'
export { default as InvoiceDetailDialog } from './InvoiceDetailDialog.vue'
export { default as CancelSubscriptionDialog } from './CancelSubscriptionDialog.vue'

// Admin billing components
export { default as CustomerDetailsDialog } from './admin/CustomerDetailsDialog.vue'
export { default as SubscriptionEditDialog } from './admin/SubscriptionEditDialog.vue'
export { default as NewSubscriptionDialog } from './admin/NewSubscriptionDialog.vue'

// Re-export types for convenience
export type {
  SubscriptionPlan,
  UserSubscription,
  Invoice
} from '@/services/billingApi'

export type {
  AdminKPIs,
  AdminSubscription,
  CustomerDetails,
  PaymentIntegrations,
  ConversionMetrics,
  APIMetrics
} from '@/services/adminBillingApi'
