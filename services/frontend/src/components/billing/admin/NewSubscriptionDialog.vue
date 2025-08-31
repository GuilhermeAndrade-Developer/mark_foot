<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="700">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>Nova Assinatura</span>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-6">
        <v-stepper v-model="currentStep" alt-labels>
          <v-stepper-header>
            <v-stepper-item title="Selecionar Cliente" value="1" />
            <v-divider />
            <v-stepper-item title="Escolher Plano" value="2" />
            <v-divider />
            <v-stepper-item title="Configurações" value="3" />
            <v-divider />
            <v-stepper-item title="Confirmação" value="4" />
          </v-stepper-header>

          <v-stepper-window>
            <!-- Step 1: Select Customer -->
            <v-stepper-window-item value="1">
              <div class="py-4">
                <h3 class="text-h6 mb-4">Selecionar Cliente</h3>
                
                <!-- Search existing users -->
                <v-text-field
                  v-model="customerSearch"
                  label="Buscar cliente existente"
                  variant="outlined"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                  @input="searchCustomers"
                />

                <!-- Customer search results -->
                <v-list v-if="searchResults.length > 0" class="border rounded mb-4" max-height="300">
                  <v-list-item
                    v-for="customer in searchResults"
                    :key="customer.id"
                    @click="selectExistingCustomer(customer)"
                    :class="{ 'v-list-item--active': selectedCustomer?.id === customer.id }"
                  >
                    <template #prepend>
                      <v-avatar size="40">
                        <v-img v-if="customer.avatar" :src="customer.avatar" />
                        <v-icon v-else icon="mdi-account" />
                      </v-avatar>
                    </template>
                    <v-list-item-title>{{ customer.full_name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ customer.email }}</v-list-item-subtitle>
                    <template #append>
                      <v-chip
                        v-if="customer.current_subscription"
                        :color="getPlanColor(customer.current_subscription.plan_type)"
                        size="small"
                        variant="tonal"
                      >
                        {{ customer.current_subscription.plan_name }}
                      </v-chip>
                    </template>
                  </v-list-item>
                </v-list>

                <!-- OR create new customer -->
                <v-divider class="my-4" />
                <div class="text-center mb-4">
                  <span class="text-body-2 text-medium-emphasis">OU</span>
                </div>

                <v-expansion-panels variant="accordion">
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon icon="mdi-account-plus" class="mr-2" />
                      Criar Novo Cliente
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="newCustomer.first_name"
                            label="Nome"
                            variant="outlined"
                            required
                          />
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="newCustomer.last_name"
                            label="Sobrenome"
                            variant="outlined"
                            required
                          />
                        </v-col>
                        <v-col cols="12">
                          <v-text-field
                            v-model="newCustomer.email"
                            label="Email"
                            type="email"
                            variant="outlined"
                            required
                          />
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="newCustomer.phone"
                            label="Telefone (opcional)"
                            variant="outlined"
                          />
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="newCustomer.company"
                            label="Empresa (opcional)"
                            variant="outlined"
                          />
                        </v-col>
                        <v-col cols="12">
                          <v-btn 
                            color="primary" 
                            @click="createNewCustomer"
                            :loading="creatingCustomer"
                            :disabled="!isNewCustomerValid"
                          >
                            Criar Cliente
                          </v-btn>
                        </v-col>
                      </v-row>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-stepper-window-item>

            <!-- Step 2: Choose Plan -->
            <v-stepper-window-item value="2">
              <div class="py-4">
                <h3 class="text-h6 mb-4">Escolher Plano</h3>
                
                <v-row>
                  <v-col
                    v-for="plan in availablePlans"
                    :key="plan.id"
                    cols="12"
                    md="4"
                  >
                    <v-card
                      :class="{ 'border-primary': selectedPlan?.id === plan.id }"
                      :variant="selectedPlan?.id === plan.id ? 'outlined' : 'elevated'"
                      @click="selectPlan(plan)"
                      class="cursor-pointer h-100"
                    >
                      <v-card-text class="text-center pa-6">
                        <v-icon
                          :icon="getPlanIcon(plan.plan_type)"
                          :color="getPlanColor(plan.plan_type)"
                          size="48"
                          class="mb-3"
                        />
                        <h4 class="text-h6 font-weight-bold mb-2">{{ plan.name }}</h4>
                        <div class="text-h4 font-weight-bold text-primary mb-1">
                          R$ {{ formatCurrency(plan.price_monthly) }}
                        </div>
                        <div class="text-body-2 text-medium-emphasis mb-3">/mês</div>
                        
                        <v-chip
                          :color="getPlanColor(plan.plan_type)"
                          variant="tonal"
                          class="mb-3"
                        >
                          {{ plan.plan_type.charAt(0).toUpperCase() + plan.plan_type.slice(1) }}
                        </v-chip>

                        <div class="text-left">
                          <div class="text-body-2 mb-2">
                            <v-icon icon="mdi-api" size="16" class="mr-1" />
                            {{ plan.api_calls_limit.toLocaleString() }} API calls/mês
                          </div>
                          
                          <div v-if="plan.advanced_ai_analysis" class="text-body-2 mb-2">
                            <v-icon icon="mdi-brain" size="16" class="mr-1" color="success" />
                            Análises IA Avançadas
                          </div>
                          
                          <div v-if="plan.unlimited_reports" class="text-body-2 mb-2">
                            <v-icon icon="mdi-file-chart" size="16" class="mr-1" color="success" />
                            Relatórios Ilimitados
                          </div>
                          
                          <div v-if="plan.white_label" class="text-body-2 mb-2">
                            <v-icon icon="mdi-palette" size="16" class="mr-1" color="success" />
                            White Label
                          </div>
                          
                          <div v-if="plan.dedicated_support" class="text-body-2 mb-2">
                            <v-icon icon="mdi-headset" size="16" class="mr-1" color="success" />
                            Suporte Dedicado
                          </div>
                          
                          <div v-if="plan.multi_tenancy" class="text-body-2">
                            <v-icon icon="mdi-office-building" size="16" class="mr-1" color="success" />
                            Multi-tenancy
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-stepper-window-item>

            <!-- Step 3: Configuration -->
            <v-stepper-window-item value="3">
              <div class="py-4">
                <h3 class="text-h6 mb-4">Configurações da Assinatura</h3>
                
                <v-row>
                  <v-col cols="12" md="6">
                    <v-select
                      v-model="subscriptionConfig.billing_cycle"
                      :items="billingCycleOptions"
                      label="Ciclo de Cobrança"
                      variant="outlined"
                    />
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="subscriptionConfig.start_date"
                      label="Data de Início"
                      type="date"
                      variant="outlined"
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="subscriptionConfig.auto_renewal"
                      label="Renovação Automática"
                      color="primary"
                      inset
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-switch
                      v-model="subscriptionConfig.starts_immediately"
                      label="Iniciar Imediatamente"
                      color="primary"
                      inset
                    />
                  </v-col>

                  <!-- Advanced Options -->
                  <v-col cols="12">
                    <v-expansion-panels variant="accordion">
                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          <v-icon icon="mdi-cog" class="mr-2" />
                          Configurações Avançadas
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <v-row>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model="subscriptionConfig.custom_price"
                                label="Preço Customizado (opcional)"
                                type="number"
                                step="0.01"
                                variant="outlined"
                                prefix="R$"
                              />
                            </v-col>
                            <v-col cols="12" md="6">
                              <v-text-field
                                v-model="subscriptionConfig.trial_days"
                                label="Dias de Trial (opcional)"
                                type="number"
                                variant="outlined"
                              />
                            </v-col>
                            <v-col cols="12">
                              <v-textarea
                                v-model="subscriptionConfig.admin_notes"
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
                </v-row>
              </div>
            </v-stepper-window-item>

            <!-- Step 4: Confirmation -->
            <v-stepper-window-item value="4">
              <div class="py-4">
                <h3 class="text-h6 mb-4">Confirmação</h3>
                
                <v-card variant="outlined" class="mb-4">
                  <v-card-text>
                    <div class="d-flex align-center mb-4">
                      <v-avatar size="48" class="mr-3">
                        <v-img v-if="selectedCustomer?.avatar" :src="selectedCustomer.avatar" />
                        <v-icon v-else icon="mdi-account" />
                      </v-avatar>
                      <div>
                        <div class="text-h6">{{ selectedCustomer?.full_name }}</div>
                        <div class="text-body-2 text-medium-emphasis">{{ selectedCustomer?.email }}</div>
                      </div>
                    </div>

                    <v-divider class="mb-4" />

                    <div class="d-flex justify-space-between mb-2">
                      <span>Plano:</span>
                      <span class="font-weight-bold">{{ selectedPlan?.name }}</span>
                    </div>
                    
                    <div class="d-flex justify-space-between mb-2">
                      <span>Valor:</span>
                      <span class="font-weight-bold">
                        R$ {{ formatCurrency(finalPrice) }}/
                        {{ subscriptionConfig.billing_cycle === 'monthly' ? 'mês' : 'ano' }}
                      </span>
                    </div>
                    
                    <div class="d-flex justify-space-between mb-2">
                      <span>Ciclo:</span>
                      <span>{{ subscriptionConfig.billing_cycle === 'monthly' ? 'Mensal' : 'Anual' }}</span>
                    </div>
                    
                    <div class="d-flex justify-space-between mb-2">
                      <span>Início:</span>
                      <span>{{ formatDate(subscriptionConfig.start_date) }}</span>
                    </div>
                    
                    <div class="d-flex justify-space-between mb-2">
                      <span>Renovação Automática:</span>
                      <span>{{ subscriptionConfig.auto_renewal ? 'Sim' : 'Não' }}</span>
                    </div>

                    <div v-if="subscriptionConfig.trial_days" class="d-flex justify-space-between mb-2">
                      <span>Trial:</span>
                      <span>{{ subscriptionConfig.trial_days }} dias</span>
                    </div>
                  </v-card-text>
                </v-card>

                <v-alert v-if="subscriptionConfig.custom_price" type="warning" variant="tonal">
                  Preço customizado será aplicado: R$ {{ formatCurrency(parseFloat(subscriptionConfig.custom_price || '0')) }}
                </v-alert>
              </div>
            </v-stepper-window-item>
          </v-stepper-window>

          <!-- Navigation Buttons -->
          <v-card-actions class="px-6 pb-6">
            <v-btn
              v-if="currentStep > 1"
              @click="currentStep--"
            >
              Voltar
            </v-btn>
            <v-spacer />
            <v-btn
              v-if="currentStep < 4"
              color="primary"
              @click="currentStep++"
              :disabled="!canProceed"
            >
              Próximo
            </v-btn>
            <v-btn
              v-if="currentStep === 4"
              color="success"
              @click="createSubscription"
              :loading="creating"
            >
              Criar Assinatura
            </v-btn>
          </v-card-actions>
        </v-stepper>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { adminBillingApi } from '@/services/adminBillingApi'
import { billingApi, type SubscriptionPlan } from '@/services/billingApi'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'created': []
}>()

// Reactive data
const currentStep = ref(1)
const creating = ref(false)
const creatingCustomer = ref(false)
const customerSearch = ref('')
const searchResults = ref([])
const availablePlans = ref<SubscriptionPlan[]>([])

const selectedCustomer = ref(null)
const selectedPlan = ref<SubscriptionPlan | null>(null)

const newCustomer = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  company: ''
})

const subscriptionConfig = ref({
  billing_cycle: 'monthly',
  start_date: new Date().toISOString().split('T')[0],
  auto_renewal: true,
  starts_immediately: true,
  custom_price: '',
  trial_days: '',
  admin_notes: ''
})

// Options
const billingCycleOptions = [
  { title: 'Mensal', value: 'monthly' },
  { title: 'Anual', value: 'yearly' }
]

// Computed
const isNewCustomerValid = computed(() => {
  return newCustomer.value.first_name && 
         newCustomer.value.last_name && 
         newCustomer.value.email
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return selectedCustomer.value !== null
    case 2:
      return selectedPlan.value !== null
    case 3:
      return true // Configuration step is always valid
    default:
      return false
  }
})

const finalPrice = computed(() => {
  if (subscriptionConfig.value.custom_price) {
    return parseFloat(subscriptionConfig.value.custom_price)
  }
  
  if (!selectedPlan.value) return 0
  
  return subscriptionConfig.value.billing_cycle === 'monthly' 
    ? selectedPlan.value.price_monthly 
    : selectedPlan.value.price_yearly
})

// Methods
const loadPlans = async () => {
  try {
    const plans = await billingApi.getPlans()
    availablePlans.value = plans
  } catch (error) {
    console.error('Error loading plans:', error)
  }
}

const searchCustomers = async () => {
  if (customerSearch.value.length < 2) {
    searchResults.value = []
    return
  }
  
  try {
    const response = await adminBillingApi.getSubscriptions(1, customerSearch.value)
    // Extract unique customers from subscriptions
    const customerMap = new Map()
    response.results.forEach(sub => {
      if (!customerMap.has(sub.user.id)) {
        customerMap.set(sub.user.id, {
          ...sub.user,
          current_subscription: {
            plan_name: sub.plan.name,
            plan_type: sub.plan.plan_type
          }
        })
      }
    })
    searchResults.value = Array.from(customerMap.values())
  } catch (error) {
    console.error('Error searching customers:', error)
  }
}

const selectExistingCustomer = (customer: any) => {
  selectedCustomer.value = customer
}

const createNewCustomer = async () => {
  creatingCustomer.value = true
  try {
    // This would typically create a new user
    // For now, we'll simulate it
    const customer = {
      id: Date.now(), // Temporary ID
      full_name: `${newCustomer.value.first_name} ${newCustomer.value.last_name}`,
      email: newCustomer.value.email,
      phone: newCustomer.value.phone,
      company: newCustomer.value.company
    }
    
    selectedCustomer.value = customer
    
    // Reset form
    newCustomer.value = {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      company: ''
    }
  } catch (error) {
    console.error('Error creating customer:', error)
  } finally {
    creatingCustomer.value = false
  }
}

const selectPlan = (plan: SubscriptionPlan) => {
  selectedPlan.value = plan
}

const createSubscription = async () => {
  if (!selectedCustomer.value || !selectedPlan.value) return
  
  creating.value = true
  try {
    const data = {
      user_id: selectedCustomer.value.id,
      plan_id: selectedPlan.value.id,
      billing_cycle: subscriptionConfig.value.billing_cycle,
      starts_immediately: subscriptionConfig.value.starts_immediately,
      auto_renewal: subscriptionConfig.value.auto_renewal,
      start_date: subscriptionConfig.value.start_date,
      custom_price: subscriptionConfig.value.custom_price ? parseFloat(subscriptionConfig.value.custom_price) : undefined,
      trial_days: subscriptionConfig.value.trial_days ? parseInt(subscriptionConfig.value.trial_days) : undefined,
      admin_notes: subscriptionConfig.value.admin_notes
    }
    
    await adminBillingApi.createSubscription(data)
    
    emit('created')
    emit('update:modelValue', false)
    resetForm()
  } catch (error) {
    console.error('Error creating subscription:', error)
  } finally {
    creating.value = false
  }
}

const resetForm = () => {
  currentStep.value = 1
  selectedCustomer.value = null
  selectedPlan.value = null
  customerSearch.value = ''
  searchResults.value = []
  
  newCustomer.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company: ''
  }
  
  subscriptionConfig.value = {
    billing_cycle: 'monthly',
    start_date: new Date().toISOString().split('T')[0],
    auto_renewal: true,
    starts_immediately: true,
    custom_price: '',
    trial_days: '',
    admin_notes: ''
  }
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

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    loadPlans()
  } else {
    resetForm()
  }
})

// Lifecycle
onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.border-primary {
  border: 2px solid rgb(var(--v-theme-primary));
}

.v-dialog >>> .v-card {
  border-radius: 12px;
}
</style>
