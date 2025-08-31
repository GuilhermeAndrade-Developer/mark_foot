<template>
  <div class="gestao-planos">
    <!-- Plans Overview Cards -->
    <v-row class="mb-6">
      <v-col
        v-for="plan in plans"
        :key="plan.id"
        cols="12"
        md="4"
      >
        <v-card
          class="h-100"
          :class="{ 'border-success': plan.plan_type === 'premium' }"
          elevation="2"
        >
          <v-card-text class="pa-6">
            <div class="d-flex justify-space-between align-center mb-4">
              <div class="d-flex align-center">
                <v-icon
                  :icon="getPlanIcon(plan.plan_type)"
                  :color="getPlanColor(plan.plan_type)"
                  size="32"
                  class="mr-3"
                />
                <div>
                  <h3 class="text-h6 font-weight-bold">{{ plan.name }}</h3>
                  <v-chip
                    :color="getPlanColor(plan.plan_type)"
                    variant="tonal"
                    size="small"
                  >
                    {{ plan.plan_type.charAt(0).toUpperCase() + plan.plan_type.slice(1) }}
                  </v-chip>
                </div>
              </div>
              
              <v-menu>
                <template #activator="{ props }">
                  <v-btn
                    icon="mdi-dots-vertical"
                    variant="text"
                    size="small"
                    v-bind="props"
                  />
                </template>
                <v-list>
                  <v-list-item @click="editPlan(plan)">
                    <template #prepend>
                      <v-icon icon="mdi-pencil" />
                    </template>
                    <v-list-item-title>Editar</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="duplicatePlan(plan)">
                    <template #prepend>
                      <v-icon icon="mdi-content-copy" />
                    </template>
                    <v-list-item-title>Duplicar</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="togglePlanStatus(plan)" :disabled="plan.plan_type === 'free'">
                    <template #prepend>
                      <v-icon :icon="plan.is_active ? 'mdi-pause' : 'mdi-play'" />
                    </template>
                    <v-list-item-title>
                      {{ plan.is_active ? 'Desativar' : 'Ativar' }}
                    </v-list-item-title>
                  </v-list-item>
                  <v-divider />
                  <v-list-item @click="deletePlan(plan)" color="error" :disabled="plan.plan_type === 'free'">
                    <template #prepend>
                      <v-icon icon="mdi-delete" />
                    </template>
                    <v-list-item-title>Excluir</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>

            <div class="mb-4">
              <p class="text-body-2 text-medium-emphasis mb-3">{{ plan.description }}</p>
              
              <!-- Pricing -->
              <div class="d-flex align-center justify-space-between mb-3">
                <div>
                  <div class="text-h4 font-weight-bold text-primary">
                    R$ {{ formatCurrency(plan.price_monthly) }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis">/mês</div>
                </div>
                <div v-if="plan.price_yearly > 0" class="text-right">
                  <div class="text-h6 font-weight-bold">
                    R$ {{ formatCurrency(plan.price_yearly) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">/ano</div>
                  <v-chip color="success" variant="tonal" size="x-small">
                    {{ Math.round((1 - (plan.price_yearly / (plan.price_monthly * 12))) * 100) }}% OFF
                  </v-chip>
                </div>
              </div>
            </div>

            <!-- Features -->
            <div class="mb-4">
              <div class="text-body-2 font-weight-medium mb-2">Características principais:</div>
              <div class="d-flex flex-column ga-1">
                <div class="d-flex align-center">
                  <v-icon icon="mdi-api" size="16" class="mr-2" color="primary" />
                  <span class="text-body-2">{{ plan.api_calls_limit.toLocaleString() }} API calls/mês</span>
                </div>
                
                <div v-if="plan.advanced_ai_analysis" class="d-flex align-center">
                  <v-icon icon="mdi-brain" size="16" class="mr-2" color="success" />
                  <span class="text-body-2">Análises IA Avançadas</span>
                </div>
                
                <div v-if="plan.unlimited_reports" class="d-flex align-center">
                  <v-icon icon="mdi-file-chart" size="16" class="mr-2" color="success" />
                  <span class="text-body-2">Relatórios Ilimitados</span>
                </div>
                
                <div v-if="plan.white_label" class="d-flex align-center">
                  <v-icon icon="mdi-palette" size="16" class="mr-2" color="success" />
                  <span class="text-body-2">White Label</span>
                </div>
                
                <div v-if="plan.dedicated_support" class="d-flex align-center">
                  <v-icon icon="mdi-headset" size="16" class="mr-2" color="success" />
                  <span class="text-body-2">Suporte Dedicado</span>
                </div>
                
                <div v-if="plan.multi_tenancy" class="d-flex align-center">
                  <v-icon icon="mdi-office-building" size="16" class="mr-2" color="success" />
                  <span class="text-body-2">Multi-tenancy</span>
                </div>
              </div>
            </div>

            <!-- Status and Stats -->
            <div class="d-flex justify-space-between align-center">
              <div>
                <v-chip
                  :color="plan.is_active ? 'success' : 'error'"
                  variant="tonal"
                  size="small"
                >
                  {{ plan.is_active ? 'Ativo' : 'Inativo' }}
                </v-chip>
              </div>
              <div class="text-right">
                <div class="text-body-2 font-weight-bold">{{ planStats[plan.id]?.subscribers || 0 }}</div>
                <div class="text-caption text-medium-emphasis">assinantes</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Plans Table -->
    <v-card elevation="2">
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Todos os Planos</span>
        <div class="d-flex ga-2">
          <v-text-field
            v-model="searchQuery"
            placeholder="Buscar planos..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            style="max-width: 300px;"
          />
          <v-btn color="success" variant="outlined" @click="exportPlans">
            <v-icon icon="mdi-download" />
            Exportar
          </v-btn>
        </div>
      </v-card-title>

      <v-data-table
        :items="filteredPlans"
        :headers="planHeaders"
        :loading="loading"
        item-value="id"
        class="elevation-0"
      >
        <template #item.name="{ item }">
          <div class="d-flex align-center">
            <v-icon
              :icon="getPlanIcon(item.plan_type)"
              :color="getPlanColor(item.plan_type)"
              size="24"
              class="mr-3"
            />
            <div>
              <div class="text-body-1 font-weight-medium">{{ item.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.plan_type }}</div>
            </div>
          </div>
        </template>

        <template #item.pricing="{ item }">
          <div>
            <div class="text-body-1 font-weight-bold">R$ {{ formatCurrency(item.price_monthly) }}/mês</div>
            <div v-if="item.price_yearly > 0" class="text-caption text-medium-emphasis">
              R$ {{ formatCurrency(item.price_yearly) }}/ano
            </div>
          </div>
        </template>

        <template #item.features="{ item }">
          <div class="d-flex flex-wrap ga-1">
            <v-chip v-if="item.advanced_ai_analysis" size="x-small" color="primary">IA</v-chip>
            <v-chip v-if="item.unlimited_reports" size="x-small" color="info">Relatórios</v-chip>
            <v-chip v-if="item.white_label" size="x-small" color="warning">White Label</v-chip>
            <v-chip v-if="item.dedicated_support" size="x-small" color="success">Suporte</v-chip>
            <v-chip v-if="item.multi_tenancy" size="x-small" color="purple">Multi-tenant</v-chip>
          </div>
        </template>

        <template #item.subscribers="{ item }">
          <div class="text-center">
            <div class="text-h6 font-weight-bold">{{ planStats[item.id]?.subscribers || 0 }}</div>
            <div class="text-caption text-medium-emphasis">assinantes</div>
          </div>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            variant="tonal"
            size="small"
          >
            {{ item.is_active ? 'Ativo' : 'Inativo' }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewPlanDetails(item)"
            />
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="editPlan(item)"
            />
            <v-btn
              icon="mdi-content-copy"
              size="small"
              variant="text"
              @click="duplicatePlan(item)"
            />
            <v-btn
              v-if="item.plan_type !== 'free'"
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deletePlan(item)"
            />
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create/Edit Plan Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="800" scrollable>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ editingPlan ? 'Editar Plano' : 'Criar Novo Plano' }}</span>
          <v-btn icon="mdi-close" variant="text" @click="closeDialog" />
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-6">
          <v-form @submit.prevent="savePlan">
            <v-row>
              <!-- Basic Info -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="planForm.name"
                  label="Nome do Plano"
                  variant="outlined"
                  required
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="planForm.plan_type"
                  :items="planTypeOptions"
                  label="Tipo do Plano"
                  variant="outlined"
                  required
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="planForm.description"
                  label="Descrição"
                  variant="outlined"
                  rows="3"
                />
              </v-col>

              <!-- Pricing -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="planForm.price_monthly"
                  label="Preço Mensal"
                  variant="outlined"
                  type="number"
                  step="0.01"
                  prefix="R$"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="planForm.price_yearly"
                  label="Preço Anual"
                  variant="outlined"
                  type="number"
                  step="0.01"
                  prefix="R$"
                />
              </v-col>

              <!-- Limits -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="planForm.api_calls_limit"
                  label="Limite de API Calls/mês"
                  variant="outlined"
                  type="number"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="planForm.sort_order"
                  label="Ordem de Exibição"
                  variant="outlined"
                  type="number"
                />
              </v-col>

              <!-- Features -->
              <v-col cols="12">
                <v-divider class="mb-4" />
                <h4 class="text-h6 mb-4">Recursos Inclusos</h4>
                
                <v-row>
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.advanced_ai_analysis"
                      label="Análises IA Avançadas"
                      color="primary"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.unlimited_reports"
                      label="Relatórios Ilimitados"
                      color="primary"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.white_label"
                      label="White Label"
                      color="primary"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.dedicated_support"
                      label="Suporte Dedicado"
                      color="primary"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.multi_tenancy"
                      label="Multi-tenancy"
                      color="primary"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-checkbox
                      v-model="planForm.is_active"
                      label="Plano Ativo"
                      color="success"
                    />
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn @click="closeDialog">Cancelar</v-btn>
          <v-btn color="primary" @click="savePlan" :loading="saving">
            {{ editingPlan ? 'Salvar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Plan Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="600">
      <v-card v-if="selectedPlan">
        <v-card-title>Detalhes do Plano - {{ selectedPlan.name }}</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h4 class="text-h6 mb-2">Informações Básicas</h4>
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>Nome:</v-list-item-title>
                  <template #append>{{ selectedPlan.name }}</template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Tipo:</v-list-item-title>
                  <template #append>{{ selectedPlan.plan_type }}</template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Preço Mensal:</v-list-item-title>
                  <template #append>R$ {{ formatCurrency(selectedPlan.price_monthly) }}</template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Preço Anual:</v-list-item-title>
                  <template #append>R$ {{ formatCurrency(selectedPlan.price_yearly) }}</template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>API Calls:</v-list-item-title>
                  <template #append>{{ selectedPlan.api_calls_limit.toLocaleString() }}/mês</template>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDetailsDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { billingApi, type SubscriptionPlan } from '@/services/billingApi'

// Emits
const emit = defineEmits(['create-plan'])

// Reactive data
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const plans = ref<SubscriptionPlan[]>([])
const planStats = ref<Record<number, { subscribers: number }>>({})

// Dialog states
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const editingPlan = ref<SubscriptionPlan | null>(null)
const selectedPlan = ref<SubscriptionPlan | null>(null)

// Form data
const planForm = ref({
  name: '',
  plan_type: 'premium',
  description: '',
  price_monthly: 0,
  price_yearly: 0,
  api_calls_limit: 1000,
  sort_order: 1,
  advanced_ai_analysis: false,
  unlimited_reports: false,
  white_label: false,
  dedicated_support: false,
  multi_tenancy: false,
  is_active: true
})

// Options
const planTypeOptions = [
  { title: 'Free', value: 'free' },
  { title: 'Premium', value: 'premium' },
  { title: 'Enterprise', value: 'enterprise' },
  { title: 'Custom', value: 'custom' }
]

// Table headers
const planHeaders = [
  { title: 'Plano', key: 'name', sortable: true },
  { title: 'Preços', key: 'pricing', sortable: false },
  { title: 'API Calls', key: 'api_calls_limit', sortable: true },
  { title: 'Recursos', key: 'features', sortable: false },
  { title: 'Assinantes', key: 'subscribers', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Computed
const filteredPlans = computed(() => {
  if (!searchQuery.value) return plans.value
  
  const search = searchQuery.value.toLowerCase()
  return plans.value.filter(plan => 
    plan.name.toLowerCase().includes(search) ||
    plan.description?.toLowerCase().includes(search) ||
    plan.plan_type.toLowerCase().includes(search)
  )
})

// Methods
const loadPlans = async () => {
  loading.value = true
  try {
    // Mock data based on seeders
    plans.value = [
      {
        id: 1,
        name: 'Free',
        plan_type: 'free',
        description: 'Plano gratuito para testes e uso pessoal',
        price_monthly: 0,
        price_yearly: 0,
        api_calls_limit: 100,
        sort_order: 1,
        advanced_ai_analysis: false,
        unlimited_reports: false,
        white_label: false,
        dedicated_support: false,
        multi_tenancy: false,
        is_active: true,
        features: {
          basic_stats: true,
          match_results: true,
          team_info: true
        }
      },
      {
        id: 2,
        name: 'Premium',
        plan_type: 'premium',
        description: 'Plano para pequenas e médias empresas',
        price_monthly: 19.90,
        price_yearly: 199.00,
        api_calls_limit: 10000,
        sort_order: 2,
        advanced_ai_analysis: true,
        unlimited_reports: false,
        white_label: false,
        dedicated_support: false,
        multi_tenancy: false,
        is_active: true,
        features: {
          basic_stats: true,
          match_results: true,
          team_info: true,
          player_stats: true,
          advanced_analytics: true
        }
      },
      {
        id: 3,
        name: 'Enterprise',
        plan_type: 'enterprise',
        description: 'Plano para grandes organizações e desenvolvedores',
        price_monthly: 499.00,
        price_yearly: 4990.00,
        api_calls_limit: 100000,
        sort_order: 3,
        advanced_ai_analysis: true,
        unlimited_reports: true,
        white_label: true,
        dedicated_support: true,
        multi_tenancy: true,
        is_active: true,
        features: {
          basic_stats: true,
          match_results: true,
          team_info: true,
          player_stats: true,
          advanced_analytics: true,
          real_time_data: true,
          custom_webhooks: true,
          priority_support: true
        }
      }
    ]

    planStats.value = {
      1: { subscribers: 150 }, // Free plan
      2: { subscribers: 45 },  // Premium plan  
      3: { subscribers: 8 }    // Enterprise plan
    }
  } catch (error) {
    console.error('Error loading plans:', error)
  } finally {
    loading.value = false
  }
}

const editPlan = (plan: SubscriptionPlan) => {
  editingPlan.value = plan
  planForm.value = {
    name: plan.name,
    plan_type: plan.plan_type,
    description: plan.description || '',
    price_monthly: plan.price_monthly,
    price_yearly: plan.price_yearly,
    api_calls_limit: plan.api_calls_limit,
    sort_order: plan.sort_order || 1,
    advanced_ai_analysis: plan.advanced_ai_analysis,
    unlimited_reports: plan.unlimited_reports,
    white_label: plan.white_label,
    dedicated_support: plan.dedicated_support,
    multi_tenancy: plan.multi_tenancy,
    is_active: plan.is_active
  }
  showCreateDialog.value = true
}

const duplicatePlan = (plan: SubscriptionPlan) => {
  editingPlan.value = null
  planForm.value = {
    name: `${plan.name} (Cópia)`,
    plan_type: 'custom',
    description: plan.description || '',
    price_monthly: plan.price_monthly,
    price_yearly: plan.price_yearly,
    api_calls_limit: plan.api_calls_limit,
    sort_order: (plan.sort_order || 1) + 1,
    advanced_ai_analysis: plan.advanced_ai_analysis,
    unlimited_reports: plan.unlimited_reports,
    white_label: plan.white_label,
    dedicated_support: plan.dedicated_support,
    multi_tenancy: plan.multi_tenancy,
    is_active: false
  }
  showCreateDialog.value = true
}

const viewPlanDetails = (plan: SubscriptionPlan) => {
  selectedPlan.value = plan
  showDetailsDialog.value = true
}

const savePlan = async () => {
  saving.value = true
  try {
    console.log('Saving plan:', planForm.value)
    // Simulate save
    await new Promise(resolve => setTimeout(resolve, 1000))
    closeDialog()
    loadPlans()
  } catch (error) {
    console.error('Error saving plan:', error)
  } finally {
    saving.value = false
  }
}

const togglePlanStatus = async (plan: SubscriptionPlan) => {
  plan.is_active = !plan.is_active
}

const deletePlan = async (plan: SubscriptionPlan) => {
  if (confirm(`Tem certeza que deseja excluir o plano "${plan.name}"?`)) {
    console.log('Deleting plan:', plan.id)
    loadPlans()
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingPlan.value = null
  resetForm()
}

const resetForm = () => {
  planForm.value = {
    name: '',
    plan_type: 'premium',
    description: '',
    price_monthly: 0,
    price_yearly: 0,
    api_calls_limit: 1000,
    sort_order: 1,
    advanced_ai_analysis: false,
    unlimited_reports: false,
    white_label: false,
    dedicated_support: false,
    multi_tenancy: false,
    is_active: true
  }
}

const exportPlans = () => {
  console.log('Exporting plans...')
}

// Utility functions
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const getPlanIcon = (planType: string) => {
  const icons: Record<string, string> = {
    free: 'mdi-gift',
    premium: 'mdi-crown',
    enterprise: 'mdi-office-building',
    custom: 'mdi-cog'
  }
  return icons[planType] || 'mdi-help'
}

const getPlanColor = (planType: string) => {
  const colors: Record<string, string> = {
    free: 'success',
    premium: 'warning',
    enterprise: 'primary',
    custom: 'purple'
  }
  return colors[planType] || 'grey'
}

// Lifecycle
onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.gestao-planos {
  width: 100%;
}

.border-success {
  border: 2px solid rgb(var(--v-theme-success));
}
</style>
