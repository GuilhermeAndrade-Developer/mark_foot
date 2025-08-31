<template>
  <v-dialog
    v-model="dialog"
    max-width="800"
    scrollable
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5 font-weight-bold">Histórico de Faturas</span>
        <v-btn
          icon
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-data-table
          :items="invoices"
          :headers="headers"
          :loading="loading"
          :items-per-page="10"
          no-data-text="Nenhuma fatura encontrada"
          loading-text="Carregando faturas..."
          class="elevation-0"
        >
          <template #item.invoice_number="{ item }">
            <div class="d-flex align-center">
              <v-icon icon="mdi-receipt" size="16" class="mr-2" />
              <span class="font-weight-medium">{{ item.invoice_number }}</span>
            </div>
          </template>

          <template #item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              variant="tonal"
              size="small"
            >
              <v-icon
                :icon="getStatusIcon(item.status)"
                size="12"
                class="mr-1"
              />
              {{ getStatusText(item.status) }}
            </v-chip>
          </template>

          <template #item.total_amount="{ item }">
            <div class="text-right">
              <div class="font-weight-bold">
                R$ {{ Number(item.total_amount).toFixed(2) }}
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ item.currency }}
              </div>
            </div>
          </template>

          <template #item.issue_date="{ item }">
            <div>
              <div>{{ formatDate(item.issue_date) }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ formatTime(item.issue_date) }}
              </div>
            </div>
          </template>

          <template #item.due_date="{ item }">
            <div>
              <div>{{ formatDate(item.due_date) }}</div>
              <div
                class="text-caption"
                :class="isOverdue(item.due_date, item.status) ? 'text-error' : 'text-medium-emphasis'"
              >
                {{ getDueDateStatus(item.due_date, item.status) }}
              </div>
            </div>
          </template>

          <template #item.period="{ item }">
            <div class="text-body-2">
              <div>{{ formatDate(item.billing_period_start) }}</div>
              <div class="text-caption text-medium-emphasis">até</div>
              <div>{{ formatDate(item.billing_period_end) }}</div>
            </div>
          </template>

          <template #item.actions="{ item }">
            <div class="d-flex ga-1">
              <v-btn
                icon
                size="small"
                variant="text"
                @click="viewInvoice(item)"
              >
                <v-icon size="16">mdi-eye</v-icon>
                <v-tooltip activator="parent">Ver detalhes</v-tooltip>
              </v-btn>
              
              <v-btn
                v-if="item.status === 'paid'"
                icon
                size="small"
                variant="text"
                @click="downloadInvoice(item)"
              >
                <v-icon size="16">mdi-download</v-icon>
                <v-tooltip activator="parent">Baixar PDF</v-tooltip>
              </v-btn>

              <v-btn
                v-if="item.status === 'pending'"
                icon
                size="small"
                variant="text"
                color="primary"
                @click="payInvoice(item)"
              >
                <v-icon size="16">mdi-credit-card</v-icon>
                <v-tooltip activator="parent">Pagar agora</v-tooltip>
              </v-btn>
            </div>
          </template>

          <template #bottom>
            <div class="pa-4">
              <v-row align="center">
                <v-col cols="12" md="6">
                  <div class="d-flex align-center ga-4">
                    <!-- Summary Cards -->
                    <v-card variant="outlined" class="pa-3 flex-1">
                      <div class="text-caption text-medium-emphasis">Total Pago</div>
                      <div class="text-h6 font-weight-bold text-success">
                        R$ {{ getTotalPaid().toFixed(2) }}
                      </div>
                    </v-card>
                    
                    <v-card variant="outlined" class="pa-3 flex-1">
                      <div class="text-caption text-medium-emphasis">Pendente</div>
                      <div class="text-h6 font-weight-bold text-warning">
                        R$ {{ getTotalPending().toFixed(2) }}
                      </div>
                    </v-card>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6" class="text-right">
                  <v-btn
                    variant="outlined"
                    prepend-icon="mdi-download"
                    @click="exportInvoices"
                  >
                    Exportar Relatório
                  </v-btn>
                </v-col>
              </v-row>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Invoice Detail Dialog -->
    <InvoiceDetailDialog
      v-model="showDetailDialog"
      :invoice="selectedInvoice"
    />
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Invoice } from '@/services/billingApi'
import InvoiceDetailDialog from './InvoiceDetailDialog.vue'

// Props
interface Props {
  modelValue: boolean
  invoices: Invoice[]
  loading?: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const showDetailDialog = ref(false)
const selectedInvoice = ref<Invoice | null>(null)

// Table headers
const headers = [
  { title: 'Número', key: 'invoice_number', width: 150 },
  { title: 'Plano', key: 'subscription_plan', width: 120 },
  { title: 'Período', key: 'period', width: 150 },
  { title: 'Valor', key: 'total_amount', width: 100, align: 'right' },
  { title: 'Status', key: 'status', width: 120 },
  { title: 'Emissão', key: 'issue_date', width: 120 },
  { title: 'Vencimento', key: 'due_date', width: 120 },
  { title: 'Ações', key: 'actions', width: 120, sortable: false }
]

// Methods
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR')
}

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    paid: 'success',
    pending: 'warning',
    overdue: 'error',
    cancelled: 'grey',
    refunded: 'info'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status: string) => {
  const icons: Record<string, string> = {
    paid: 'mdi-check',
    pending: 'mdi-clock',
    overdue: 'mdi-alert',
    cancelled: 'mdi-cancel',
    refunded: 'mdi-undo'
  }
  return icons[status] || 'mdi-help'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    paid: 'Pago',
    pending: 'Pendente',
    overdue: 'Vencido',
    cancelled: 'Cancelado',
    refunded: 'Reembolsado'
  }
  return texts[status] || status
}

const isOverdue = (dueDate: string, status: string) => {
  if (status === 'paid') return false
  return new Date(dueDate) < new Date()
}

const getDueDateStatus = (dueDate: string, status: string) => {
  if (status === 'paid') return 'Pago'
  
  const due = new Date(dueDate)
  const now = new Date()
  const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return `${Math.abs(diffDays)} dias em atraso`
  if (diffDays === 0) return 'Vence hoje'
  if (diffDays <= 7) return `${diffDays} dias restantes`
  
  return 'No prazo'
}

const getTotalPaid = () => {
  return props.invoices
    .filter(invoice => invoice.status === 'paid')
    .reduce((total, invoice) => total + Number(invoice.total_amount), 0)
}

const getTotalPending = () => {
  return props.invoices
    .filter(invoice => ['pending', 'overdue'].includes(invoice.status))
    .reduce((total, invoice) => total + Number(invoice.total_amount), 0)
}

const viewInvoice = (invoice: Invoice) => {
  selectedInvoice.value = invoice
  showDetailDialog.value = true
}

const downloadInvoice = (invoice: Invoice) => {
  // TODO: Implement PDF download
  console.log('Download invoice:', invoice.invoice_number)
}

const payInvoice = (invoice: Invoice) => {
  // TODO: Implement payment flow
  console.log('Pay invoice:', invoice.invoice_number)
}

const exportInvoices = () => {
  // TODO: Implement export functionality
  console.log('Export invoices')
}
</script>

<style scoped>
.v-data-table {
  border-radius: 0;
}

.v-data-table >>> .v-data-table__wrapper {
  max-height: 600px;
}
</style>
