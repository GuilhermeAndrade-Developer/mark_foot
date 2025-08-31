<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="900" scrollable>
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Detalhes do Cliente</span>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>

      <v-divider />

      <v-card-text v-if="customer" class="pa-6">
        <!-- Customer Header -->
        <div class="d-flex align-center mb-6">
          <v-avatar size="80" class="mr-4">
            <v-img v-if="customer.avatar" :src="customer.avatar" />
            <v-icon v-else icon="mdi-account" size="48" />
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">{{ customer.full_name }}</h2>
            <div class="text-body-1 text-medium-emphasis mb-2">{{ customer.email }}</div>
            <div class="d-flex ga-2">
              <v-chip size="small" color="info">
                Cliente desde {{ formatDate(customer.created_at) }}
              </v-chip>
              <v-chip 
                v-if="customer.last_login" 
                size="small" 
                :color="isRecentLogin(customer.last_login) ? 'success' : 'warning'"
              >
                Último acesso: {{ formatRelativeTime(customer.last_login) }}
              </v-chip>
            </div>
          </div>
        </div>

        <!-- Customer Stats -->
        <v-row class="mb-6">
          <v-col cols="3">
            <v-card class="pa-4 text-center" variant="tonal" color="success">
              <div class="text-h4 font-weight-bold">R$ {{ formatCurrency(customer.lifetime_value) }}</div>
              <div class="text-body-2">Lifetime Value</div>
            </v-card>
          </v-col>
          <v-col cols="3">
            <v-card class="pa-4 text-center" variant="tonal" color="info">
              <div class="text-h4 font-weight-bold">{{ customer.subscription_history.length }}</div>
              <div class="text-body-2">Assinaturas</div>
            </v-card>
          </v-col>
          <v-col cols="3">
            <v-card class="pa-4 text-center" variant="tonal" color="warning">
              <div class="text-h4 font-weight-bold">{{ customer.payment_history.length }}</div>
              <div class="text-body-2">Pagamentos</div>
            </v-card>
          </v-col>
          <v-col cols="3">
            <v-card class="pa-4 text-center" variant="tonal" color="primary">
              <div class="text-h4 font-weight-bold">{{ customer.support_tickets }}</div>
              <div class="text-body-2">Tickets</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Tabs -->
        <v-tabs v-model="activeTab" class="mb-6">
          <v-tab value="subscription">Assinaturas</v-tab>
          <v-tab value="payments">Pagamentos</v-tab>
          <v-tab value="usage">Uso da API</v-tab>
          <v-tab value="actions">Ações</v-tab>
        </v-tabs>

        <v-tabs-window v-model="activeTab">
          <!-- Subscription History -->
          <v-tabs-window-item value="subscription">
            <v-card variant="outlined">
              <v-card-title>Histórico de Assinaturas</v-card-title>
              <v-data-table
                :items="customer.subscription_history"
                :headers="subscriptionHeaders"
                density="compact"
                no-data-text="Nenhuma assinatura encontrada"
              >
                <template #item.status="{ item }">
                  <v-chip 
                    :color="item.ended_at ? 'grey' : 'success'" 
                    size="small" 
                    variant="tonal"
                  >
                    {{ item.ended_at ? 'Finalizada' : 'Ativa' }}
                  </v-chip>
                </template>
                <template #item.revenue="{ item }">
                  R$ {{ formatCurrency(item.revenue) }}
                </template>
                <template #item.started_at="{ item }">
                  {{ formatDate(item.started_at) }}
                </template>
                <template #item.ended_at="{ item }">
                  {{ item.ended_at ? formatDate(item.ended_at) : '-' }}
                </template>
              </v-data-table>
            </v-card>
          </v-tabs-window-item>

          <!-- Payment History -->
          <v-tabs-window-item value="payments">
            <v-card variant="outlined">
              <v-card-title class="d-flex justify-space-between align-center">
                <span>Histórico de Pagamentos</span>
                <v-btn size="small" color="primary" @click="showRefundDialog = true">
                  Processar Reembolso
                </v-btn>
              </v-card-title>
              <v-data-table
                :items="customer.payment_history"
                :headers="paymentHeaders"
                density="compact"
                no-data-text="Nenhum pagamento encontrado"
              >
                <template #item.status="{ item }">
                  <v-chip 
                    :color="getPaymentStatusColor(item.status)" 
                    size="small" 
                    variant="tonal"
                  >
                    {{ getPaymentStatusText(item.status) }}
                  </v-chip>
                </template>
                <template #item.amount="{ item }">
                  R$ {{ formatCurrency(item.amount) }}
                </template>
                <template #item.created_at="{ item }">
                  {{ formatDateTime(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn
                    v-if="item.status === 'paid'"
                    icon="mdi-cash-refund"
                    size="small"
                    variant="text"
                    color="warning"
                    @click="initiateRefund(item)"
                  />
                </template>
              </v-data-table>
            </v-card>
          </v-tabs-window-item>

          <!-- API Usage -->
          <v-tabs-window-item value="usage">
            <v-card variant="outlined">
              <v-card-title>Uso da API (Últimos 30 dias)</v-card-title>
              <div class="pa-4">
                <LineChart 
                  v-if="usageChartData.datasets.length"
                  :data="usageChartData" 
                  :options="chartOptions"
                  height="300"
                />
                <div v-else class="text-center py-8">
                  <v-icon icon="mdi-chart-line" size="64" color="grey-lighten-2" class="mb-4" />
                  <p class="text-body-1 text-medium-emphasis">Nenhum uso de API nos últimos 30 dias</p>
                </div>
              </div>
            </v-card>
          </v-tabs-window-item>

          <!-- Actions -->
          <v-tabs-window-item value="actions">
            <div class="d-flex flex-column ga-4">
              <!-- Send Email -->
              <v-card variant="outlined">
                <v-card-title>Enviar Email</v-card-title>
                <v-card-text>
                  <v-form @submit.prevent="sendCustomerEmail">
                    <v-row>
                      <v-col cols="12">
                        <v-text-field
                          v-model="emailForm.subject"
                          label="Assunto"
                          variant="outlined"
                          required
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="emailForm.message"
                          label="Mensagem"
                          variant="outlined"
                          rows="4"
                          required
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-btn type="submit" color="primary" :loading="sendingEmail">
                          Enviar Email
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-form>
                </v-card-text>
              </v-card>

              <!-- Quick Actions -->
              <v-card variant="outlined">
                <v-card-title>Ações Rápidas</v-card-title>
                <v-card-text>
                  <div class="d-flex flex-wrap ga-3">
                    <v-btn color="success" @click="resetApiUsage">
                      Resetar Uso da API
                    </v-btn>
                    <v-btn color="warning" @click="suspendAccount">
                      Suspender Conta
                    </v-btn>
                    <v-btn color="info" @click="viewLoginHistory">
                      Histórico de Login
                    </v-btn>
                    <v-btn color="primary" @click="generateReport">
                      Gerar Relatório
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>

      <v-skeleton-loader v-else type="card" loading />
    </v-card>

    <!-- Refund Dialog -->
    <v-dialog :model-value="showRefundDialog" @update:model-value="showRefundDialog = $event" max-width="500">
      <v-card>
        <v-card-title>Processar Reembolso</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="processRefund">
            <v-text-field
              v-model="refundForm.amount"
              label="Valor (deixe vazio para reembolso total)"
              variant="outlined"
              type="number"
              step="0.01"
              prefix="R$"
            />
            <v-textarea
              v-model="refundForm.reason"
              label="Motivo do reembolso"
              variant="outlined"
              required
            />
            <div class="d-flex justify-end ga-2 mt-4">
              <v-btn @click="showRefundDialog = false">Cancelar</v-btn>
              <v-btn type="submit" color="warning" :loading="processingRefund">
                Processar Reembolso
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { adminBillingApi, type CustomerDetails } from '@/services/adminBillingApi'
import LineChart from '@/components/charts/LineChart.vue'

const props = defineProps<{
  modelValue: boolean
  customer: CustomerDetails | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Reactive data
const activeTab = ref('subscription')
const showRefundDialog = ref(false)
const sendingEmail = ref(false)
const processingRefund = ref(false)
const selectedPayment = ref(null)

const emailForm = ref({
  subject: '',
  message: ''
})

const refundForm = ref({
  amount: '',
  reason: ''
})

// Table headers
const subscriptionHeaders = [
  { title: 'Plano', key: 'plan_name' },
  { title: 'Status', key: 'status' },
  { title: 'Início', key: 'started_at' },
  { title: 'Fim', key: 'ended_at' },
  { title: 'Receita', key: 'revenue' }
]

const paymentHeaders = [
  { title: 'ID', key: 'id' },
  { title: 'Valor', key: 'amount' },
  { title: 'Status', key: 'status' },
  { title: 'Método', key: 'method' },
  { title: 'Data', key: 'created_at' },
  { title: 'Ações', key: 'actions' }
]

// Computed
const usageChartData = computed(() => {
  if (!props.customer?.api_usage_history) {
    return { labels: [], datasets: [] }
  }

  const labels = props.customer.api_usage_history.map(item => 
    new Date(item.date).toLocaleDateString('pt-BR')
  )
  
  const data = props.customer.api_usage_history.map(item => item.calls)
  const limits = props.customer.api_usage_history.map(item => item.limit)

  return {
    labels,
    datasets: [
      {
        label: 'Calls Utilizadas',
        data,
        borderColor: '#1976D2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true
      },
      {
        label: 'Limite',
        data: limits,
        borderColor: '#FFC107',
        backgroundColor: 'transparent',
        borderDash: [5, 5]
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Methods
const sendCustomerEmail = async () => {
  if (!props.customer) return
  
  sendingEmail.value = true
  try {
    await adminBillingApi.sendCustomerEmail(props.customer.id, emailForm.value)
    emailForm.value = { subject: '', message: '' }
    // Show success message
  } catch (error) {
    console.error('Error sending email:', error)
  } finally {
    sendingEmail.value = false
  }
}

const initiateRefund = (payment: any) => {
  selectedPayment.value = payment
  refundForm.value = {
    amount: payment.amount.toString(),
    reason: ''
  }
  showRefundDialog.value = true
}

const processRefund = async () => {
  if (!selectedPayment.value) return
  
  processingRefund.value = true
  try {
    await adminBillingApi.refundPayment(selectedPayment.value.id, {
      amount: refundForm.value.amount ? parseFloat(refundForm.value.amount) : undefined,
      reason: refundForm.value.reason,
      full_refund: !refundForm.value.amount
    })
    
    showRefundDialog.value = false
    refundForm.value = { amount: '', reason: '' }
    // Refresh customer data
  } catch (error) {
    console.error('Error processing refund:', error)
  } finally {
    processingRefund.value = false
  }
}

const resetApiUsage = async () => {
  if (!props.customer) return
  // Implement API usage reset
}

const suspendAccount = async () => {
  if (!props.customer) return
  // Implement account suspension
}

const viewLoginHistory = () => {
  // Implement login history view
}

const generateReport = async () => {
  if (!props.customer) return
  // Implement customer report generation
}

// Utility functions
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR')
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('pt-BR')
}

const formatRelativeTime = (date: string) => {
  const now = new Date()
  const past = new Date(date)
  const diffMs = now.getTime() - past.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Hoje'
  if (diffDays === 1) return 'Ontem'
  if (diffDays < 7) return `${diffDays} dias atrás`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} semanas atrás`
  return `${Math.floor(diffDays / 30)} meses atrás`
}

const isRecentLogin = (date: string) => {
  const now = new Date()
  const loginDate = new Date(date)
  const diffDays = (now.getTime() - loginDate.getTime()) / (1000 * 60 * 60 * 24)
  return diffDays <= 7
}

const getPaymentStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    paid: 'success',
    pending: 'warning',
    failed: 'error',
    refunded: 'info',
    cancelled: 'grey'
  }
  return colors[status] || 'grey'
}

const getPaymentStatusText = (status: string) => {
  const texts: Record<string, string> = {
    paid: 'Pago',
    pending: 'Pendente',
    failed: 'Falhou',
    refunded: 'Reembolsado',
    cancelled: 'Cancelado'
  }
  return texts[status] || status
}

// Watch for dialog close
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    activeTab.value = 'subscription'
    emailForm.value = { subject: '', message: '' }
  }
})
</script>

<style scoped>
.v-dialog >>> .v-card {
  border-radius: 12px;
}
</style>
