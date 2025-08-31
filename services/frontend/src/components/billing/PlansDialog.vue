<template>
  <v-dialog
    v-model="dialog"
    max-width="900"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5 font-weight-bold">Escolher Plano</span>
        <v-btn
          icon
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-6">
        <div v-if="loading" class="text-center py-8">
          <v-progress-circular
            indeterminate
            color="primary"
            size="48"
          />
          <p class="mt-4">Carregando planos...</p>
        </div>

        <div v-else>
          <!-- Billing Cycle Toggle -->
          <div class="text-center mb-6">
            <v-btn-toggle
              v-model="billingCycle"
              color="primary"
              mandatory
              variant="outlined"
            >
              <v-btn value="monthly">
                Mensal
              </v-btn>
              <v-btn value="yearly">
                Anual
                <v-chip
                  color="success"
                  size="x-small"
                  class="ml-2"
                >
                  -16%
                </v-chip>
              </v-btn>
            </v-btn-toggle>
          </div>

          <!-- Plans Grid -->
          <v-row>
            <v-col
              v-for="plan in plans"
              :key="plan.id"
              cols="12"
              md="4"
            >
              <v-card
                :elevation="currentPlan?.id === plan.id ? 0 : 2"
                :variant="currentPlan?.id === plan.id ? 'outlined' : 'elevated'"
                :color="currentPlan?.id === plan.id ? 'primary' : undefined"
                class="plan-card h-100 position-relative"
                :class="{ 'current-plan': currentPlan?.id === plan.id }"
              >
                <!-- Current Plan Badge -->
                <v-chip
                  v-if="currentPlan?.id === plan.id"
                  color="primary"
                  size="small"
                  class="position-absolute plan-badge"
                  style="top: -8px; right: 16px; z-index: 1;"
                >
                  Plano Atual
                </v-chip>

                <!-- Popular Badge -->
                <v-chip
                  v-if="plan.plan_type === 'premium'"
                  color="warning"
                  size="small"
                  class="position-absolute plan-badge"
                  style="top: -8px; left: 16px; z-index: 1;"
                >
                  Mais Popular
                </v-chip>

                <v-card-text class="pa-6 text-center">
                  <!-- Plan Icon -->
                  <v-icon
                    :icon="getPlanIcon(plan.plan_type)"
                    :color="getPlanColor(plan.plan_type)"
                    size="48"
                    class="mb-4"
                  />

                  <!-- Plan Name -->
                  <h3 class="text-h5 font-weight-bold mb-2">
                    {{ plan.name }}
                  </h3>

                  <!-- Plan Price -->
                  <div class="mb-4">
                    <div class="text-h4 font-weight-bold text-primary">
                      R$ {{ getPrice(plan).toFixed(2) }}
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      /{{ billingCycle === 'monthly' ? 'mês' : 'ano' }}
                    </div>
                    <div
                      v-if="billingCycle === 'yearly' && Number(plan.price_yearly) > 0"
                      class="text-body-2 text-success mt-1"
                    >
                      Economize R$ {{ getYearlySavings(plan).toFixed(2) }} por ano
                    </div>
                  </div>

                  <!-- Plan Description -->
                  <p class="text-body-2 text-medium-emphasis mb-4">
                    {{ plan.description }}
                  </p>

                  <!-- API Calls Limit -->
                  <div class="mb-4">
                    <v-chip
                      variant="tonal"
                      color="info"
                      size="small"
                    >
                      {{ plan.api_calls_limit === 0 ? 'Ilimitado' : plan.api_calls_limit.toLocaleString() }} 
                      API calls/mês
                    </v-chip>
                  </div>

                  <!-- Features List -->
                  <div class="text-left mb-6">
                    <div
                      v-for="(feature, index) in getPlanFeatures(plan)"
                      :key="index"
                      class="d-flex align-center mb-2"
                    >
                      <v-icon
                        :icon="feature.included ? 'mdi-check' : 'mdi-close'"
                        :color="feature.included ? 'success' : 'error'"
                        size="16"
                        class="mr-2"
                      />
                      <span
                        class="text-body-2"
                        :class="{ 'text-medium-emphasis': !feature.included }"
                      >
                        {{ feature.name }}
                      </span>
                    </div>
                  </div>

                  <!-- Action Button -->
                  <v-btn
                    v-if="currentPlan?.id === plan.id"
                    variant="outlined"
                    color="primary"
                    block
                    disabled
                  >
                    Plano Atual
                  </v-btn>
                  <v-btn
                    v-else-if="plan.plan_type === 'free'"
                    variant="outlined"
                    color="success"
                    block
                    @click="selectPlan(plan)"
                  >
                    Usar Gratuito
                  </v-btn>
                  <v-btn
                    v-else
                    color="primary"
                    block
                    @click="selectPlan(plan)"
                    :disabled="selecting"
                    :loading="selecting && selectedPlanId === plan.id"
                  >
                    {{ currentPlan && getPrice(plan) > getPrice(currentPlan) ? 'Fazer Upgrade' : 'Selecionar Plano' }}
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Features Comparison -->
          <div class="mt-8">
            <h3 class="text-h6 mb-4 text-center">Comparação de Recursos</h3>
            <v-table>
              <thead>
                <tr>
                  <th>Recurso</th>
                  <th class="text-center">Free</th>
                  <th class="text-center">Premium</th>
                  <th class="text-center">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="feature in allFeatures"
                  :key="feature.key"
                >
                  <td class="font-weight-medium">{{ feature.name }}</td>
                  <td class="text-center">
                    <v-icon
                      :icon="getFeatureIcon(feature.free)"
                      :color="feature.free ? 'success' : 'error'"
                      size="20"
                    />
                  </td>
                  <td class="text-center">
                    <v-icon
                      :icon="getFeatureIcon(feature.premium)"
                      :color="feature.premium ? 'success' : 'error'"
                      size="20"
                    />
                  </td>
                  <td class="text-center">
                    <v-icon
                      :icon="getFeatureIcon(feature.enterprise)"
                      :color="feature.enterprise ? 'success' : 'error'"
                      size="20"
                    />
                  </td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { billingApi, type SubscriptionPlan } from '@/services/billingApi'

// Props
interface Props {
  modelValue: boolean
  currentPlan?: SubscriptionPlan
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'plan-selected': [planId: number]
}>()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const selecting = ref(false)
const selectedPlanId = ref<number | null>(null)
const plans = ref<SubscriptionPlan[]>([])
const billingCycle = ref<'monthly' | 'yearly'>('monthly')

// Methods
const loadPlans = async () => {
  loading.value = true
  try {
    plans.value = await billingApi.getPlans()
  } catch (error) {
    console.error('Error loading plans:', error)
  } finally {
    loading.value = false
  }
}

const selectPlan = async (plan: SubscriptionPlan) => {
  selecting.value = true
  selectedPlanId.value = plan.id
  
  try {
    emit('plan-selected', plan.id)
  } catch (error) {
    console.error('Error selecting plan:', error)
  } finally {
    selecting.value = false
    selectedPlanId.value = null
  }
}

const getPrice = (plan: SubscriptionPlan) => {
  if (billingCycle.value === 'yearly' && Number(plan.price_yearly) > 0) {
    return Number(plan.price_yearly)
  }
  return Number(plan.price_monthly)
}

const getYearlySavings = (plan: SubscriptionPlan) => {
  const monthlyTotal = Number(plan.price_monthly) * 12
  return monthlyTotal - Number(plan.price_yearly)
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

const getPlanFeatures = (plan: SubscriptionPlan) => {
  const baseFeatures = [
    { name: 'Dados básicos', included: true },
    { name: 'Resultados de partidas', included: true },
    { name: 'Informações de times', included: true },
    { name: 'Acesso à comunidade', included: true }
  ]

  const premiumFeatures = [
    { name: 'Análises avançadas de IA', included: plan.advanced_ai_analysis },
    { name: 'Relatórios ilimitados', included: plan.unlimited_reports },
    { name: 'Suporte prioritário', included: plan.plan_type !== 'free' },
    { name: 'Exportação de dados', included: plan.plan_type !== 'free' }
  ]

  const enterpriseFeatures = [
    { name: 'White-label', included: plan.white_label },
    { name: 'Suporte dedicado', included: plan.dedicated_support },
    { name: 'Multi-tenancy', included: plan.multi_tenancy },
    { name: 'SLA garantido', included: plan.plan_type === 'enterprise' }
  ]

  return [...baseFeatures, ...premiumFeatures, ...enterpriseFeatures]
}

const getFeatureIcon = (included: boolean) => {
  return included ? 'mdi-check' : 'mdi-close'
}

// All features for comparison table
const allFeatures = [
  {
    key: 'api_calls',
    name: 'API Calls/mês',
    free: '100',
    premium: '10.000',
    enterprise: '100.000'
  },
  {
    key: 'basic_stats',
    name: 'Estatísticas básicas',
    free: true,
    premium: true,
    enterprise: true
  },
  {
    key: 'advanced_ai',
    name: 'Análises de IA',
    free: false,
    premium: true,
    enterprise: true
  },
  {
    key: 'unlimited_reports',
    name: 'Relatórios ilimitados',
    free: false,
    premium: true,
    enterprise: true
  },
  {
    key: 'white_label',
    name: 'White-label',
    free: false,
    premium: false,
    enterprise: true
  },
  {
    key: 'dedicated_support',
    name: 'Suporte dedicado',
    free: false,
    premium: false,
    enterprise: true
  },
  {
    key: 'multi_tenancy',
    name: 'Multi-tenancy',
    free: false,
    premium: false,
    enterprise: true
  }
]

// Lifecycle
onMounted(() => {
  if (props.modelValue) {
    loadPlans()
  }
})

watch(() => props.modelValue, (newValue) => {
  if (newValue && plans.value.length === 0) {
    loadPlans()
  }
})
</script>

<style scoped>
.plan-card {
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-4px);
}

.current-plan {
  border: 2px solid rgb(var(--v-theme-primary));
}

.plan-badge {
  z-index: 1;
}

.v-table th {
  font-weight: 600;
}
</style>
