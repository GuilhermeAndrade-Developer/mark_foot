// Billing module components
export { default as FinanceiroDashboard } from './FinanceiroDashboard.vue'
export { default as PlansDialog } from './PlansDialog.vue'
export { default as InvoicesDialog } from './InvoicesDialog.vue'
export { default as InvoiceDetailDialog } from './InvoiceDetailDialog.vue'
export { default as CancelSubscriptionDialog } from './CancelSubscriptionDialog.vue'

// Re-export types for convenience
export type {
  SubscriptionPlan,
  UserSubscription,
  Invoice
} from '@/services/billingApi'
