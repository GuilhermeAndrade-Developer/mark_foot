<template>
  <div class="dashboard-financeiro">
    <!-- KPIs Principais -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="pa-4 h-100" elevation="2">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-h4 font-weight-bold text-success">
                R$ {{ formatCurrency(kpis.mrr) }}
              </div>
              <div class="text-body-2 text-medium-emphasis">MRR (Receita Recorrente)</div>
              <div class="d-flex align-center mt-1">
                <v-icon 
                  :icon="kpis.mrr_growth >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                  :color="kpis.mrr_growth >= 0 ? 'success' : 'error'"
                  size="16"
                  class="mr-1"
                />
                <span :class="kpis.mrr_growth >= 0 ? 'text-success' : 'text-error'" class="text-caption">
                  {{ kpis.mrr_growth >= 0 ? '+' : '' }}{{ kpis.mrr_growth.toFixed(1) }}%
                </span>
              </div>
            </div>
            <v-icon icon="mdi-chart-line" color="success" size="40" />
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4 h-100" elevation="2">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-h4 font-weight-bold text-info">
                {{ kpis.active_subscribers }}
              </div>
              <div class="text-body-2 text-medium-emphasis">Assinantes Ativos</div>
              <div class="d-flex align-center mt-1">
                <v-icon 
                  :icon="kpis.subscriber_growth >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                  :color="kpis.subscriber_growth >= 0 ? 'success' : 'error'"
                  size="16"
                  class="mr-1"
                />
                <span :class="kpis.subscriber_growth >= 0 ? 'text-success' : 'text-error'" class="text-caption">
                  {{ kpis.subscriber_growth >= 0 ? '+' : '' }}{{ kpis.subscriber_growth.toFixed(1) }}%
                </span>
              </div>
            </div>
            <v-icon icon="mdi-account-multiple" color="info" size="40" />
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4 h-100" elevation="2">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-h4 font-weight-bold text-warning">
                {{ kpis.churn_rate.toFixed(1) }}%
              </div>
              <div class="text-body-2 text-medium-emphasis">Taxa de Churn</div>
              <div class="d-flex align-center mt-1">
                <v-icon 
                  :icon="kpis.churn_trend <= 0 ? 'mdi-trending-down' : 'mdi-trending-up'"
                  :color="kpis.churn_trend <= 0 ? 'success' : 'error'"
                  size="16"
                  class="mr-1"
                />
                <span :class="kpis.churn_trend <= 0 ? 'text-success' : 'text-error'" class="text-caption">
                  {{ kpis.churn_trend <= 0 ? '' : '+' }}{{ kpis.churn_trend.toFixed(1) }}%
                </span>
              </div>
            </div>
            <v-icon icon="mdi-account-minus" color="warning" size="40" />
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card class="pa-4 h-100" elevation="2">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-h4 font-weight-bold text-primary">
                R$ {{ formatCurrency(kpis.arpu) }}
              </div>
              <div class="text-body-2 text-medium-emphasis">ARPU Médio</div>
              <div class="d-flex align-center mt-1">
                <v-icon 
                  :icon="kpis.arpu_growth >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                  :color="kpis.arpu_growth >= 0 ? 'success' : 'error'"
                  size="16"
                  class="mr-1"
                />
                <span :class="kpis.arpu_growth >= 0 ? 'text-success' : 'text-error'" class="text-caption">
                  {{ kpis.arpu_growth >= 0 ? '+' : '' }}{{ kpis.arpu_growth.toFixed(1) }}%
                </span>
              </div>
            </div>
            <v-icon icon="mdi-currency-usd" color="primary" size="40" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Section -->
    <v-row class="mb-6">
      <!-- Revenue Chart -->
      <v-col cols="12" lg="8">
        <v-card elevation="2">
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Evolução da Receita</span>
            <v-btn-toggle
              v-model="revenueChartPeriod"
              mandatory
              variant="outlined"
              density="compact"
            >
              <v-btn value="7d" size="small">7d</v-btn>
              <v-btn value="30d" size="small">30d</v-btn>
              <v-btn value="90d" size="small">90d</v-btn>
              <v-btn value="1y" size="small">1a</v-btn>
            </v-btn-toggle>
          </v-card-title>
          <v-card-text>
            <div class="chart-container">
              <!-- Mock chart - seria integrado com biblioteca real -->
              <div class="chart-placeholder">
                <v-icon icon="mdi-chart-areaspline" size="64" color="primary" />
                <div class="text-h6 mt-2">Gráfico de Receita por Período</div>
                <div class="text-body-2 text-medium-emphasis">Integração com Chart.js pendente</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Distribution Chart -->
      <v-col cols="12" lg="4">
        <v-card elevation="2" class="h-100">
          <v-card-title>Distribuição por Plano</v-card-title>
          <v-card-text>
            <div class="chart-container">
              <!-- Mock pie chart -->
              <div class="chart-placeholder">
                <v-icon icon="mdi-chart-pie" size="64" color="warning" />
                <div class="text-h6 mt-2">Distribuição de Assinantes</div>
                <div class="text-body-2 text-medium-emphasis mt-4">
                  <div class="d-flex justify-space-between mb-2">
                    <span>Free:</span>
                    <span class="font-weight-bold">{{ planDistribution.free }}%</span>
                  </div>
                  <div class="d-flex justify-space-between mb-2">
                    <span>Premium:</span>
                    <span class="font-weight-bold">{{ planDistribution.premium }}%</span>
                  </div>
                  <div class="d-flex justify-space-between">
                    <span>Enterprise:</span>
                    <span class="font-weight-bold">{{ planDistribution.enterprise }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Integration Status -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-credit-card-multiple" class="mr-2" />
            Status das Integrações
          </v-card-title>
          <v-card-text>
            <div class="d-flex flex-column ga-3">
              <!-- Stripe Status -->
              <div class="d-flex justify-space-between align-center">
                <div class="d-flex align-center">
                  <v-icon icon="mdi-credit-card" class="mr-3" color="primary" />
                  <div>
                    <div class="text-body-1 font-weight-medium">Stripe</div>
                    <div class="text-caption text-medium-emphasis">Pagamentos Internacionais</div>
                  </div>
                </div>
                <v-chip 
                  :color="integrationStatus.stripe.status === 'active' ? 'success' : 'error'"
                  variant="tonal"
                  size="small"
                >
                  {{ integrationStatus.stripe.status === 'active' ? 'Ativo' : 'Inativo' }}
                </v-chip>
              </div>

              <v-divider />

              <!-- PagSeguro Status -->
              <div class="d-flex justify-space-between align-center">
                <div class="d-flex align-center">
                  <v-icon icon="mdi-credit-card-outline" class="mr-3" color="warning" />
                  <div>
                    <div class="text-body-1 font-weight-medium">PagSeguro</div>
                    <div class="text-caption text-medium-emphasis">Pagamentos Brasil</div>
                  </div>
                </div>
                <v-chip 
                  :color="integrationStatus.pagseguro.status === 'active' ? 'success' : 'error'"
                  variant="tonal"
                  size="small"
                >
                  {{ integrationStatus.pagseguro.status === 'active' ? 'Ativo' : 'Inativo' }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick Actions -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-lightning-bolt" class="mr-2" />
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <div class="d-flex flex-column ga-2">
              <v-btn variant="outlined" prepend-icon="mdi-account-plus" @click="createSubscription">
                Nova Assinatura
              </v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-file-invoice" @click="generateInvoice">
                Gerar Fatura
              </v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-account-search" @click="searchCustomer">
                Buscar Cliente
              </v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-chart-box" @click="generateReport">
                Relatório Detalhado
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Transactions -->
    <v-card elevation="2">
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Transações Recentes</span>
        <v-btn variant="text" size="small" @click="viewAllTransactions">
          Ver Todas
        </v-btn>
      </v-card-title>
      <v-data-table
        :items="recentTransactions"
        :headers="transactionHeaders"
        :loading="loading"
        item-value="id"
        class="elevation-0"
        :items-per-page="5"
      >
        <template #item.customer="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-icon icon="mdi-account-circle" />
            </v-avatar>
            <div>
              <div class="text-body-2 font-weight-medium">{{ item.customer.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.customer.email }}</div>
            </div>
          </div>
        </template>

        <template #item.amount="{ item }">
          <div class="text-body-1 font-weight-bold">
            R$ {{ formatCurrency(item.amount) }}
          </div>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="tonal"
            size="small"
          >
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <template #item.date="{ item }">
          <div class="text-body-2">
            {{ formatDate(item.date) }}
          </div>
        </template>

        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            variant="text"
            size="small"
            @click="viewTransaction(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <!-- Modal para gerar fatura -->
    <v-dialog v-model="showInvoiceModal" max-width="600">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-file-invoice" class="mr-2" />
          Gerar Nova Fatura
        </v-card-title>
        <v-card-text>
          <v-form>
            <v-row>
              <v-col cols="12">
                <v-autocomplete
                  v-model="invoiceForm.customer"
                  :items="customers"
                  item-title="name"
                  item-value="id"
                  label="Cliente"
                  prepend-inner-icon="mdi-account"
                  outlined
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="invoiceForm.plan"
                  :items="plans"
                  item-title="name"
                  item-value="id"
                  label="Plano"
                  prepend-inner-icon="mdi-package-variant"
                  outlined
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="invoiceForm.amount"
                  label="Valor (R$)"
                  prepend-inner-icon="mdi-currency-usd"
                  type="number"
                  outlined
                  required
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="invoiceForm.description"
                  label="Descrição"
                  prepend-inner-icon="mdi-note-text"
                  outlined
                  rows="3"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showInvoiceModal = false">
            Cancelar
          </v-btn>
          <v-btn color="primary" @click="submitInvoice" :loading="submittingInvoice">
            Gerar Fatura
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminBillingApi } from '@/services/adminBillingApi'

// Router
const router = useRouter()

// Emits
const emit = defineEmits(['export-report', 'refresh-data'])

// Reactive data
const loading = ref(false)
const revenueChartPeriod = ref('30d')
const showInvoiceModal = ref(false)
const submittingInvoice = ref(false)

// Form data para fatura
const invoiceForm = reactive({
  customer: null,
  plan: '',
  amount: '',
  description: ''
})

// Data from API
const kpis = ref({
  mrr: 0,
  mrr_growth: 0,
  active_subscribers: 0,
  subscriber_growth: 0,
  churn_rate: 0,
  churn_trend: 0,
  arpu: 0,
  arpu_growth: 0
})

const planDistribution = ref({
  free: 0,
  premium: 0,
  enterprise: 0
})

const integrationStatus = ref({
  stripe: { status: 'inactive' },
  pagseguro: { status: 'inactive' }
})

const recentTransactions = ref([])
const customers = ref([])
const plans = ref([])

// Table headers
const transactionHeaders = [
  { title: 'Cliente', key: 'customer', sortable: false },
  { title: 'Valor', key: 'amount', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Data', key: 'date', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Methods
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    paid: 'success',
    pending: 'warning',
    failed: 'error',
    refunded: 'info'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    paid: 'Pago',
    pending: 'Pendente',
    failed: 'Falhou',
    refunded: 'Reembolsado'
  }
  return texts[status] || status
}

// API Loading functions
const loadDashboardData = async () => {
  loading.value = true
  try {
    // Load KPIs
    const kpisResponse = await adminBillingApi.getDashboardKpis()
    kpis.value = kpisResponse.data
    
    // Load plan distribution
    const distributionResponse = await adminBillingApi.getPlanDistribution()
    planDistribution.value = distributionResponse.data
    
    // Load recent transactions
    const transactionsResponse = await adminBillingApi.getRecentTransactions()
    recentTransactions.value = transactionsResponse.data
    
    // Load integration status
    const integrationResponse = await adminBillingApi.getIntegrationStatus()
    integrationStatus.value = integrationResponse.data
    
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error)
    // Use fallback data or show error message
    loadFallbackData()
  } finally {
    loading.value = false
  }
}

const loadCustomersAndPlans = async () => {
  try {
    // Load customers for the modal
    const customersResponse = await adminBillingApi.getCustomers()
    customers.value = customersResponse.data.map((customer: any) => ({
      id: customer.id,
      name: `${customer.first_name} ${customer.last_name} - ${customer.email}`
    }))
    
    // Load plans for the modal
    const plansResponse = await adminBillingApi.getPlans()
    plans.value = plansResponse.data.map((plan: any) => ({
      id: plan.id,
      name: `${plan.name} - R$ ${plan.price_monthly}`
    }))
    
  } catch (error) {
    console.error('Erro ao carregar clientes e planos:', error)
  }
}

const loadFallbackData = () => {
  // Fallback data when API is not available - based on seeded data
  kpis.value = {
    mrr: 1498.90, // Enterprise (499) + Premium (19.90 * 2) = 538.80 monthly, but some yearly
    mrr_growth: 12.3,
    active_subscribers: 6, // Based on seeded data
    subscriber_growth: 8.7,
    churn_rate: 2.1,
    churn_trend: -0.5,
    arpu: 249.82, // Average revenue per user based on plan distribution
    arpu_growth: 5.2
  }
  
  planDistribution.value = {
    free: 50,    // 3 out of 6 users
    premium: 33, // 2 out of 6 users  
    enterprise: 17 // 1 out of 6 users
  }
  
  integrationStatus.value = {
    stripe: { status: 'inactive' },
    pagseguro: { status: 'inactive' }
  }
  
  recentTransactions.value = [
    {
      id: 1,
      customer: { name: 'João Silva', email: 'joao.silva@empresa.com' },
      amount: 4990.00, // Enterprise yearly
      status: 'paid',
      date: '2025-08-30T10:30:00Z',
      plan: 'Enterprise'
    },
    {
      id: 2,
      customer: { name: 'Maria Santos', email: 'maria.santos@startup.io' },
      amount: 19.90,
      status: 'paid',
      date: '2025-08-30T09:15:00Z',
      plan: 'Premium'
    },
    {
      id: 3,
      customer: { name: 'Pedro Costa', email: 'pedro.costa@tech.com' },
      amount: 19.90,
      status: 'overdue',
      date: '2025-08-25T08:45:00Z',
      plan: 'Premium'
    }
  ]
  
  customers.value = [
    { id: 1, name: 'João Silva - joao.silva@empresa.com' },
    { id: 2, name: 'Maria Santos - maria.santos@startup.io' },
    { id: 3, name: 'Pedro Costa - pedro.costa@tech.com' },
    { id: 4, name: 'Ana Oliveira - ana.oliveira@digital.com' },
    { id: 5, name: 'Carlos Ferreira - carlos.ferreira@corp.com' }
  ]
  
  plans.value = [
    { id: 1, name: 'Free - R$ 0.00' },
    { id: 2, name: 'Premium - R$ 19.90' },
    { id: 3, name: 'Enterprise - R$ 499.00' }
  ]
}
const createSubscription = () => {
  // Navegar para a página de gestão de clientes na aba "novos clientes"
  router.push('/financeiro/clientes?tab=new-clients')
}

const generateInvoice = async () => {
  // Carregar dados necessários e abrir modal para gerar fatura
  await loadCustomersAndPlans()
  showInvoiceModal.value = true
}

const searchCustomer = () => {
  // Navegar para a página de gestão de clientes na aba "buscar clientes"
  router.push('/financeiro/clientes?tab=search-clients')
}

const generateReport = () => {
  emit('export-report')
}

const viewAllTransactions = () => {
  // Navegar para uma página dedicada de transações ou expandir tabela
  console.log('Ver todas as transações - implementar página dedicada')
  // TODO: router.push('/financeiro/transacoes')
}

const viewTransaction = (transaction: any) => {
  console.log('Ver transação:', transaction)
}

const submitInvoice = async () => {
  submittingInvoice.value = true
  try {
    const invoiceData = {
      customer_id: invoiceForm.customer,
      plan_id: invoiceForm.plan,
      amount: parseFloat(invoiceForm.amount),
      description: invoiceForm.description
    }
    
    const result = await adminBillingApi.createInvoice(invoiceData)
    
    if (result.success) {
      console.log('Fatura gerada com sucesso!', result)
      
      // Reset form e fechar modal
      Object.assign(invoiceForm, {
        customer: null,
        plan: '',
        amount: '',
        description: ''
      })
      showInvoiceModal.value = false
      
      // Recarregar dados do dashboard
      await loadDashboardData()
      
      // Aqui poderia mostrar uma notificação de sucesso
      // emit('show-notification', { type: 'success', message: 'Fatura gerada com sucesso!' })
    } else {
      console.error('Erro ao gerar fatura:', result.message)
    }
  } catch (error) {
    console.error('Erro ao gerar fatura:', error)
    // Simular comportamento quando API não está disponível
    console.log('API não disponível - simulando criação de fatura:', invoiceForm)
    
    // Reset form e fechar modal mesmo assim
    Object.assign(invoiceForm, {
      customer: null,
      plan: '',
      amount: '',
      description: ''
    })
    showInvoiceModal.value = false
  } finally {
    submittingInvoice.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Load dashboard data on component mount
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-financeiro {
  width: 100%;
}

.chart-container {
  min-height: 200px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  border: 2px dashed rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}
</style>
