<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Editar Assinatura</span>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>

      <v-divider />

      <v-card-text v-if="subscription" class="pa-6">
        <!-- Customer Info -->
        <div class="d-flex align-center mb-6 pa-4 bg-grey-lighten-5 rounded">
          <v-avatar size="48" class="mr-3">
            <v-img v-if="subscription.user.avatar" :src="subscription.user.avatar" />
            <v-icon v-else icon="mdi-account" />
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-bold">{{ subscription.user.full_name }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ subscription.user.email }}</div>
          </div>
        </div>

        <v-form @submit.prevent="saveChanges">
          <v-row>
            <!-- Plan Selection -->
            <v-col cols="12">
              <v-select
                v-model="formData.plan_id"
                :items="availablePlans"
                item-title="name"
                item-value="id"
                label="Plano"
                variant="outlined"
                @update:model-value="onPlanChange"
              >
                <template #item="{ props, item }">
                  <v-list-item v-bind="props">
                    <template #prepend>
                      <v-icon 
                        :icon="getPlanIcon(item.raw.plan_type)" 
                        :color="getPlanColor(item.raw.plan_type)"
                      />
                    </template>
                    <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      R$ {{ formatCurrency(item.raw.price_monthly) }}/mês
                    </v-list-item-subtitle>
                    <template #append>
                      <v-chip 
                        :color="getPlanColor(item.raw.plan_type)" 
                        variant="tonal" 
                        size="small"
                      >
                        {{ item.raw.plan_type }}
                      </v-chip>
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>

            <!-- Status -->
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.status"
                :items="statusOptions"
                label="Status"
                variant="outlined"
              />
            </v-col>

            <!-- Billing Cycle -->
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.billing_cycle"
                :items="billingCycleOptions"
                label="Ciclo de Cobrança"
                variant="outlined"
              />
            </v-col>

            <!-- Expires At -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.expires_at"
                label="Data de Expiração"
                type="date"
                variant="outlined"
              />
            </v-col>

            <!-- Auto Renewal -->
            <v-col cols="12" md="6">
              <v-switch
                v-model="formData.auto_renewal"
                label="Renovação Automática"
                color="primary"
                inset
              />
            </v-col>

            <!-- Price Override (Admin only) -->
            <v-col cols="12">
              <v-expansion-panels variant="accordion">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <v-icon icon="mdi-cash-edit" class="mr-2" />
                    Configurações Avançadas
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="formData.custom_price"
                          label="Preço Customizado (deixe vazio para usar padrão)"
                          type="number"
                          step="0.01"
                          variant="outlined"
                          prefix="R$"
                        />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="formData.api_calls_override"
                          label="Limite de API Calls (deixe vazio para usar padrão)"
                          type="number"
                          variant="outlined"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="formData.admin_notes"
                          label="Notas Administrativas"
                          variant="outlined"
                          rows="3"
                        />
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-col>

            <!-- Plan Comparison -->
            <v-col v-if="selectedPlan && selectedPlan.id !== subscription.plan.id" cols="12">
              <v-alert type="info" variant="tonal">
                <v-alert-title>Mudança de Plano</v-alert-title>
                <div class="mt-2">
                  <div class="d-flex justify-space-between mb-2">
                    <span>Plano Atual:</span>
                    <span class="font-weight-bold">
                      {{ subscription.plan.name }} - R$ {{ formatCurrency(subscription.plan.price_monthly) }}/mês
                    </span>
                  </div>
                  <div class="d-flex justify-space-between mb-2">
                    <span>Novo Plano:</span>
                    <span class="font-weight-bold">
                      {{ selectedPlan.name }} - R$ {{ formatCurrency(selectedPlan.price_monthly) }}/mês
                    </span>
                  </div>
                  <v-divider class="my-2" />
                  <div class="d-flex justify-space-between">
                    <span>Diferença:</span>
                    <span 
                      :class="priceDifference >= 0 ? 'text-success' : 'text-error'"
                      class="font-weight-bold"
                    >
                      {{ priceDifference >= 0 ? '+' : '' }}R$ {{ formatCurrency(Math.abs(priceDifference)) }}/mês
                      ({{ priceDifference >= 0 ? 'Upgrade' : 'Downgrade' }})
                    </span>
                  </div>
                </div>
              </v-alert>
            </v-col>

            <!-- Action Buttons -->
            <v-col cols="12">
              <div class="d-flex justify-end ga-3">
                <v-btn @click="$emit('update:modelValue', false)">
                  Cancelar
                </v-btn>
                <v-btn 
                  type="submit" 
                  color="primary" 
                  :loading="saving"
                  :disabled="!hasChanges"
                >
                  Salvar Alterações
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-form>

        <!-- Subscription History -->
        <v-divider class="my-6" />
        <h3 class="text-h6 mb-4">Histórico de Mudanças</h3>
        <v-timeline density="compact" align="start">
          <v-timeline-item
            v-for="(change, index) in subscriptionHistory"
            :key="index"
            :dot-color="getChangeColor(change.type)"
            size="small"
          >
            <template #icon>
              <v-icon :icon="getChangeIcon(change.type)" size="16" />
            </template>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-body-2 font-weight-medium">{{ change.description }}</div>
                <div class="text-caption text-medium-emphasis">{{ change.reason }}</div>
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ formatDateTime(change.created_at) }}
              </div>
            </div>
          </v-timeline-item>
        </v-timeline>
      </v-card-text>

      <v-skeleton-loader v-else type="card" loading />
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { adminBillingApi, type AdminSubscription } from '@/services/adminBillingApi'
import { billingApi, type SubscriptionPlan } from '@/services/billingApi'

const props = defineProps<{
  modelValue: boolean
  subscription: AdminSubscription | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'updated': []
}>()

// Reactive data
const saving = ref(false)
const availablePlans = ref<SubscriptionPlan[]>([])
const subscriptionHistory = ref([])

const formData = ref({
  plan_id: 0,
  status: '',
  billing_cycle: '',
  expires_at: '',
  auto_renewal: false,
  custom_price: '',
  api_calls_override: '',
  admin_notes: ''
})

const originalData = ref({})

// Options
const statusOptions = [
  { title: 'Ativo', value: 'active' },
  { title: 'Cancelado', value: 'cancelled' },
  { title: 'Expirado', value: 'expired' },
  { title: 'Pendente', value: 'pending' },
  { title: 'Suspenso', value: 'suspended' }
]

const billingCycleOptions = [
  { title: 'Mensal', value: 'monthly' },
  { title: 'Anual', value: 'yearly' }
]

// Computed
const selectedPlan = computed(() => 
  availablePlans.value.find(plan => plan.id === formData.value.plan_id)
)

const priceDifference = computed(() => {
  if (!props.subscription || !selectedPlan.value) return 0
  return selectedPlan.value.price_monthly - props.subscription.plan.price_monthly
})

const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value)
})

// Methods
const loadData = async () => {
  try {
    // Load available plans
    const plans = await billingApi.getPlans()
    availablePlans.value = plans
    
    // Load subscription history if needed
    if (props.subscription) {
      // subscriptionHistory.value = await adminBillingApi.getSubscriptionHistory(props.subscription.id)
    }
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

const resetForm = () => {
  if (!props.subscription) return
  
  const data = {
    plan_id: props.subscription.plan.id,
    status: props.subscription.status,
    billing_cycle: props.subscription.billing_cycle,
    expires_at: props.subscription.expires_at.split('T')[0], // Format for date input
    auto_renewal: props.subscription.auto_renewal || false,
    custom_price: '',
    api_calls_override: '',
    admin_notes: ''
  }
  
  formData.value = { ...data }
  originalData.value = { ...data }
}

const onPlanChange = () => {
  // Could trigger additional logic when plan changes
}

const saveChanges = async () => {
  if (!props.subscription) return
  
  saving.value = true
  try {
    const updateData: any = {
      plan_id: formData.value.plan_id,
      status: formData.value.status,
      billing_cycle: formData.value.billing_cycle,
      expires_at: formData.value.expires_at,
      auto_renewal: formData.value.auto_renewal
    }

    // Add custom fields if specified
    if (formData.value.custom_price) {
      updateData.custom_price = parseFloat(formData.value.custom_price)
    }
    
    if (formData.value.api_calls_override) {
      updateData.api_calls_limit = parseInt(formData.value.api_calls_override)
    }
    
    if (formData.value.admin_notes) {
      updateData.admin_notes = formData.value.admin_notes
    }

    await adminBillingApi.updateSubscription(props.subscription.id, updateData)
    
    emit('updated')
    emit('update:modelValue', false)
  } catch (error) {
    console.error('Error updating subscription:', error)
  } finally {
    saving.value = false
  }
}

// Utility functions
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('pt-BR')
}

const getPlanIcon = (planType: string) => {
  const icons: Record<string, string> = {
    free: 'mdi-gift',
    premium: 'mdi-crown',
    enterprise: 'mdi-office-building'
  }
  return icons[planType] || 'mdi-help'
}

const getPlanColor = (planType: string) => {
  const colors: Record<string, string> = {
    free: 'success',
    premium: 'warning',
    enterprise: 'primary'
  }
  return colors[planType] || 'grey'
}

const getChangeColor = (type: string) => {
  const colors: Record<string, string> = {
    upgrade: 'success',
    downgrade: 'warning',
    cancellation: 'error',
    renewal: 'info',
    created: 'primary'
  }
  return colors[type] || 'grey'
}

const getChangeIcon = (type: string) => {
  const icons: Record<string, string> = {
    upgrade: 'mdi-trending-up',
    downgrade: 'mdi-trending-down',
    cancellation: 'mdi-cancel',
    renewal: 'mdi-refresh',
    created: 'mdi-plus'
  }
  return icons[type] || 'mdi-information'
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue && props.subscription) {
    resetForm()
    loadData()
  }
})

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-dialog >>> .v-card {
  border-radius: 12px;
}

.bg-grey-lighten-5 {
  background-color: #fafafa;
}
</style>
