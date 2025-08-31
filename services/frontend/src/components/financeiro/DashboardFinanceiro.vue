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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminBillingApi } from '@/services/adminBillingApi'

// Emits
const emit = defineEmits(['export-report', 'refresh-data'])

// Reactive data
const loading = ref(false)
const revenueChartPeriod = ref('30d')

// KPIs mock data
const kpis = ref({
  mrr: 15420.50,
  mrr_growth: 12.3,
  active_subscribers: 203,
  subscriber_growth: 8.7,
  churn_rate: 2.1,
  churn_trend: -0.5,
  arpu: 75.85,
  arpu_growth: 5.2
})

// Plan distribution mock data
const planDistribution = ref({
  free: 74,
  premium: 22,
  enterprise: 4
})

// Integration status mock data
const integrationStatus = ref({
  stripe: { status: 'active' },
  pagseguro: { status: 'active' }
})

// Recent transactions mock data
const recentTransactions = ref([
  {
    id: 1,
    customer: { name: 'João Silva', email: 'joao@empresa.com' },
    amount: 19.90,
    status: 'paid',
    date: '2025-08-30T10:30:00Z',
    plan: 'Premium'
  },
  {
    id: 2,
    customer: { name: 'Maria Santos', email: 'maria@startup.io' },
    amount: 499.00,
    status: 'paid',
    date: '2025-08-30T09:15:00Z',
    plan: 'Enterprise'
  },
  {
    id: 3,
    customer: { name: 'Pedro Costa', email: 'pedro@tech.com' },
    amount: 19.90,
    status: 'pending',
    date: '2025-08-30T08:45:00Z',
    plan: 'Premium'
  }
])

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

// Action methods
const createSubscription = () => {
  console.log('Criar nova assinatura')
}

const generateInvoice = () => {
  console.log('Gerar fatura')
}

const searchCustomer = () => {
  console.log('Buscar cliente')
}

const generateReport = () => {
  emit('export-report')
}

const viewAllTransactions = () => {
  console.log('Ver todas as transações')
}

const viewTransaction = (transaction: any) => {
  console.log('Ver transação:', transaction)
}

// Lifecycle
onMounted(() => {
  // Load dashboard data
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
