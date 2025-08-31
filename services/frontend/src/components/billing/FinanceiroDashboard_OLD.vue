<template>
  <div class="financial-dashboard">
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Financeiro</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gestão de planos, assinaturas e faturamento
        </p>
      </div>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="showUpgradeDialog = true"
      >
        Upgrade Plano
      </v-btn>
    </div>

    <!-- Current Subscription Card -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="pa-6" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <div>
              <h3 class="text-h6 mb-2">Assinatura Atual</h3>
              <v-chip
                :color="getStatusColor(currentSubscription?.status)"
                variant="tonal"
                size="small"
              >
                {{ getStatusText(currentSubscription?.status) }}
              </v-chip>
            </div>
            <v-icon
              :icon="getPlanIcon(currentSubscription?.plan?.plan_type)"
              :color="getPlanColor(currentSubscription?.plan?.plan_type)"
              size="40"
            />
          </div>

          <div v-if="currentSubscription">
            <div class="d-flex justify-space-between align-center mb-3">
              <div>
                <h4 class="text-h5 font-weight-bold">
                  {{ currentSubscription.plan.name }}
                </h4>
                <p class="text-body-2 text-medium-emphasis">
                  {{ currentSubscription.plan.description }}
                </p>
              </div>
              <div class="text-right">
                <h4 class="text-h5 font-weight-bold text-primary">
                  R$ {{ Number(currentSubscription.plan.price_monthly).toFixed(2) }}
                </h4>
                <p class="text-body-2 text-medium-emphasis">/mês</p>
              </div>
            </div>

            <!-- API Usage Progress -->
            <div class="mb-4">
              <div class="d-flex justify-space-between align-center mb-2">
                <span class="text-body-2 font-weight-medium">Uso da API</span>
                <span class="text-body-2 text-medium-emphasis">
                  {{ currentSubscription.api_calls_used.toLocaleString() }} / 
                  {{ currentSubscription.plan.api_calls_limit.toLocaleString() }} calls
                </span>
              </div>
              <v-progress-linear
                :model-value="currentSubscription.api_usage_percentage"
                :color="getUsageColor(currentSubscription.api_usage_percentage)"
                height="8"
                rounded
              />
              <div class="d-flex justify-space-between mt-1">
                <span class="text-caption text-medium-emphasis">
                  {{ currentSubscription.api_calls_remaining.toLocaleString() }} restantes
                </span>
                <span class="text-caption text-medium-emphasis">
                  Reset: {{ formatDate(currentSubscription.api_calls_reset_date) }}
                </span>
              </div>
            </div>

            <!-- Subscription Details -->
            <v-row>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h6 font-weight-bold">
                    {{ currentSubscription.days_remaining }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Dias restantes</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h6 font-weight-bold">
                    {{ currentSubscription.billing_cycle === 'monthly' ? 'Mensal' : 'Anual' }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Ciclo</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <v-icon
                    :icon="currentSubscription.auto_renewal ? 'mdi-autorenew' : 'mdi-autorenew-off'"
                    :color="currentSubscription.auto_renewal ? 'success' : 'warning'"
                  />
                  <div class="text-caption text-medium-emphasis">Auto-renovação</div>
                </div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-center">
                  <div class="text-h6 font-weight-bold">
                    {{ formatDate(currentSubscription.expires_at) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Expira em</div>
                </div>
              </v-col>
            </v-row>
          </div>

          <v-skeleton-loader
            v-else
            type="card"
            loading
          />
        </v-card>
      </v-col>
    </v-row>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center" elevation="1">
          <v-icon icon="mdi-api" color="primary" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">
            {{ usageSummary?.monthly_usage?.toLocaleString() || '0' }}
          </div>
          <div class="text-body-2 text-medium-emphasis">Calls este mês</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center" elevation="1">
          <v-icon icon="mdi-receipt" color="success" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">
            {{ invoices?.length || '0' }}
          </div>
          <div class="text-body-2 text-medium-emphasis">Faturas</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center" elevation="1">
          <v-icon icon="mdi-chart-line" color="warning" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">
            {{ currentSubscription?.api_usage_percentage?.toFixed(1) || '0' }}%
          </div>
          <div class="text-body-2 text-medium-emphasis">Uso da API</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center" elevation="1">
          <v-icon icon="mdi-calendar-clock" color="info" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">
            {{ currentSubscription?.days_remaining || '0' }}
          </div>
          <div class="text-body-2 text-medium-emphasis">Dias restantes</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Usage Chart -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card class="pa-6" elevation="2">
          <h3 class="text-h6 mb-4">Uso da API por Endpoint</h3>
          <div v-if="usageSummary?.usage_by_endpoint?.length">
            <div
              v-for="(endpoint, index) in usageSummary.usage_by_endpoint.slice(0, 5)"
              :key="index"
              class="mb-3"
            >
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-body-2">{{ endpoint.endpoint }}</span>
                <span class="text-body-2 font-weight-bold">{{ endpoint.count }}</span>
              </div>
              <v-progress-linear
                :model-value="(endpoint.count / usageSummary.usage_by_endpoint[0].count) * 100"
                color="primary"
                height="6"
                rounded
              />
            </div>
          </div>
          <div v-else class="text-center py-8">
            <v-icon icon="mdi-chart-box-outline" size="64" color="grey-lighten-1" class="mb-4" />
            <p class="text-body-1 text-medium-emphasis">Nenhum uso de API registrado</p>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-6" elevation="2">
          <h3 class="text-h6 mb-4">Ações Rápidas</h3>
          <div class="d-flex flex-column ga-3">
            <v-btn
              variant="outlined"
              color="primary"
              prepend-icon="mdi-upgrade"
              @click="showUpgradeDialog = true"
            >
              Upgrade de Plano
            </v-btn>
            <v-btn
              variant="outlined"
              color="info"
              prepend-icon="mdi-receipt-text"
              @click="showInvoicesDialog = true"
            >
              Ver Faturas
            </v-btn>
            <v-btn
              variant="outlined"
              color="warning"
              prepend-icon="mdi-cancel"
              @click="showCancelDialog = true"
              :disabled="currentSubscription?.plan?.plan_type === 'free'"
            >
              Cancelar Assinatura
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Invoices -->
    <v-row>
      <v-col cols="12">
        <v-card class="pa-6" elevation="2">
          <div class="d-flex justify-space-between align-center mb-4">
            <h3 class="text-h6">Faturas Recentes</h3>
            <v-btn
              variant="outlined"
              size="small"
              @click="showInvoicesDialog = true"
            >
              Ver Todas
            </v-btn>
          </div>
          
          <v-data-table
            :items="invoices?.slice(0, 5) || []"
            :headers="invoiceHeaders"
            :loading="loadingInvoices"
            no-data-text="Nenhuma fatura encontrada"
            loading-text="Carregando faturas..."
          >
            <template #item.status="{ item }">
              <v-chip
                :color="getInvoiceStatusColor(item.status)"
                variant="tonal"
                size="small"
              >
                {{ getInvoiceStatusText(item.status) }}
              </v-chip>
            </template>
            <template #item.total_amount="{ item }">
              R$ {{ Number(item.total_amount).toFixed(2) }}
            </template>
            <template #item.issue_date="{ item }">
              {{ formatDate(item.issue_date) }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upgrade Dialog -->
    <PlansDialog
      v-model="showUpgradeDialog"
      :current-plan="currentSubscription?.plan"
      @plan-selected="handlePlanChange"
    />

    <!-- Invoices Dialog -->
    <InvoicesDialog
      v-model="showInvoicesDialog"
      :invoices="invoices"
      :loading="loadingInvoices"
    />

    <!-- Cancel Dialog -->
    <CancelSubscriptionDialog
      v-model="showCancelDialog"
      :subscription="currentSubscription"
      @cancelled="handleSubscriptionCancelled"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { billingApi, type UserSubscription, type Invoice, type ApiUsageSummary } from '@/services/billingApi'
import PlansDialog from '@/components/billing/PlansDialog.vue'
import InvoicesDialog from '@/components/billing/InvoicesDialog.vue'
import CancelSubscriptionDialog from '@/components/billing/CancelSubscriptionDialog.vue'

// Reactive data
const loading = ref(false)
const loadingInvoices = ref(false)
const currentSubscription = ref<UserSubscription | null>(null)
const invoices = ref<Invoice[]>([])
const usageSummary = ref<ApiUsageSummary | null>(null)

// Dialog states
const showUpgradeDialog = ref(false)
const showInvoicesDialog = ref(false)
const showCancelDialog = ref(false)

// Table headers
const invoiceHeaders = [
  { title: 'Número', key: 'invoice_number' },
  { title: 'Plano', key: 'subscription_plan' },
  { title: 'Valor', key: 'total_amount' },
  { title: 'Status', key: 'status' },
  { title: 'Data', key: 'issue_date' }
]

// Methods
const loadData = async () => {
  loading.value = true
  try {
    const [subscription, invoicesData, usage] = await Promise.all([
      billingApi.getCurrentSubscription(),
      billingApi.getInvoices(),
      billingApi.getUsageSummary()
    ])
    
    currentSubscription.value = subscription
    invoices.value = invoicesData
    usageSummary.value = usage
  } catch (error) {
    console.error('Error loading billing data:', error)
  } finally {
    loading.value = false
  }
}

const handlePlanChange = async (planId: number) => {
  if (!currentSubscription.value) return
  
  try {
    const updatedSubscription = await billingApi.changePlan(
      currentSubscription.value.id,
      planId,
      'Upgrade via dashboard'
    )
    currentSubscription.value = updatedSubscription
    showUpgradeDialog.value = false
  } catch (error) {
    console.error('Error changing plan:', error)
  }
}

const handleSubscriptionCancelled = (subscription: UserSubscription) => {
  currentSubscription.value = subscription
  showCancelDialog.value = false
}

// Utility functions
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR')
}

const getStatusColor = (status?: string) => {
  const colors: Record<string, string> = {
    active: 'success',
    cancelled: 'warning',
    expired: 'error',
    pending: 'info',
    suspended: 'error'
  }
  return colors[status || 'info'] || 'grey'
}

const getStatusText = (status?: string) => {
  const texts: Record<string, string> = {
    active: 'Ativo',
    cancelled: 'Cancelado',
    expired: 'Expirado',
    pending: 'Pendente',
    suspended: 'Suspenso'
  }
  return texts[status || 'info'] || 'Desconhecido'
}

const getPlanIcon = (planType?: string) => {
  const icons: Record<string, string> = {
    free: 'mdi-gift',
    premium: 'mdi-crown',
    enterprise: 'mdi-office-building'
  }
  return icons[planType || 'free'] || 'mdi-help'
}

const getPlanColor = (planType?: string) => {
  const colors: Record<string, string> = {
    free: 'success',
    premium: 'warning',
    enterprise: 'primary'
  }
  return colors[planType || 'free'] || 'grey'
}

const getUsageColor = (percentage: number) => {
  if (percentage < 50) return 'success'
  if (percentage < 80) return 'warning'
  return 'error'
}

const getInvoiceStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    paid: 'success',
    pending: 'warning',
    overdue: 'error',
    cancelled: 'grey'
  }
  return colors[status] || 'grey'
}

const getInvoiceStatusText = (status: string) => {
  const texts: Record<string, string> = {
    paid: 'Pago',
    pending: 'Pendente',
    overdue: 'Vencido',
    cancelled: 'Cancelado'
  }
  return texts[status] || status
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.financial-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.v-progress-linear {
  border-radius: 4px;
}
</style>
