<template>
  <div class="configuracoes-financeiras">
    <v-row>
      <!-- Stripe Configuration -->
      <v-col cols="12" md="6">
        <v-card class="pa-6" elevation="2">
          <div class="d-flex align-center mb-4">
            <div class="stripe-logo mr-3">
              <v-icon icon="mdi-credit-card" size="32" color="primary" />
            </div>
            <div>
              <h3 class="text-h6 font-weight-bold">Integração Stripe</h3>
              <p class="text-body-2 text-medium-emphasis">Para pagamentos internacionais com cartão</p>
            </div>
          </div>

          <v-form>
            <v-switch
              v-model="stripeConfig.enabled"
              label="Habilitar Stripe"
              color="primary"
              inset
              class="mb-4"
            />

            <div v-if="stripeConfig.enabled">
              <v-select
                v-model="stripeConfig.environment"
                :items="environmentOptions"
                label="Ambiente"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="stripeConfig.publishable_key"
                label="Publishable Key"
                variant="outlined"
                :type="showStripeKeys ? 'text' : 'password'"
                class="mb-4"
              />

              <v-text-field
                v-model="stripeConfig.secret_key"
                label="Secret Key"
                variant="outlined"
                :type="showStripeKeys ? 'text' : 'password'"
                class="mb-4"
              />

              <v-text-field
                v-model="stripeConfig.webhook_secret"
                label="Webhook Endpoint Secret"
                variant="outlined"
                :type="showStripeKeys ? 'text' : 'password'"
                class="mb-4"
              />

              <div class="d-flex justify-space-between align-center mb-4">
                <v-btn
                  variant="outlined"
                  @click="showStripeKeys = !showStripeKeys"
                  :prepend-icon="showStripeKeys ? 'mdi-eye-off' : 'mdi-eye'"
                >
                  {{ showStripeKeys ? 'Ocultar' : 'Mostrar' }} Chaves
                </v-btn>
                
                <v-btn
                  color="info"
                  variant="outlined"
                  @click="testStripeConnection"
                  :loading="testingStripe"
                >
                  Testar Conexão
                </v-btn>
              </div>

              <!-- Webhook URL -->
              <v-alert type="info" variant="tonal" class="mb-4">
                <v-alert-title>URL do Webhook</v-alert-title>
                <div class="mt-2">
                  <code>{{ stripeWebhookUrl }}</code>
                  <v-btn
                    icon="mdi-content-copy"
                    size="small"
                    variant="text"
                    @click="copyToClipboard(stripeWebhookUrl)"
                    class="ml-2"
                  />
                </div>
              </v-alert>

              <!-- Supported Events -->
              <v-expansion-panels variant="accordion">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    Eventos do Webhook Configurados
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-chip-group>
                      <v-chip
                        v-for="event in stripeWebhookEvents"
                        :key="event"
                        size="small"
                        variant="tonal"
                      >
                        {{ event }}
                      </v-chip>
                    </v-chip-group>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </v-form>
        </v-card>
      </v-col>

      <!-- PagSeguro Configuration -->
      <v-col cols="12" md="6">
        <v-card class="pa-6" elevation="2">
          <div class="d-flex align-center mb-4">
            <div class="pagseguro-logo mr-3">
              <v-icon icon="mdi-credit-card-outline" size="32" color="warning" />
            </div>
            <div>
              <h3 class="text-h6 font-weight-bold">Integração PagSeguro</h3>
              <p class="text-body-2 text-medium-emphasis">Para pagamentos no Brasil (PIX, Boleto, Cartão)</p>
            </div>
          </div>

          <v-form>
            <v-switch
              v-model="pagseguroConfig.enabled"
              label="Habilitar PagSeguro"
              color="warning"
              inset
              class="mb-4"
            />

            <div v-if="pagseguroConfig.enabled">
              <v-select
                v-model="pagseguroConfig.environment"
                :items="environmentOptions"
                label="Ambiente"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="pagseguroConfig.app_id"
                label="App ID"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="pagseguroConfig.app_key"
                label="App Key"
                variant="outlined"
                :type="showPagSeguroKeys ? 'text' : 'password'"
                class="mb-4"
              />

              <v-text-field
                v-model="pagseguroConfig.token"
                label="Token"
                variant="outlined"
                :type="showPagSeguroKeys ? 'text' : 'password'"
                class="mb-4"
              />

              <div class="d-flex justify-space-between align-center mb-4">
                <v-btn
                  variant="outlined"
                  @click="showPagSeguroKeys = !showPagSeguroKeys"
                  :prepend-icon="showPagSeguroKeys ? 'mdi-eye-off' : 'mdi-eye'"
                >
                  {{ showPagSeguroKeys ? 'Ocultar' : 'Mostrar' }} Chaves
                </v-btn>
                
                <v-btn
                  color="info"
                  variant="outlined"
                  @click="testPagSeguroConnection"
                  :loading="testingPagSeguro"
                >
                  Testar Conexão
                </v-btn>
              </div>

              <!-- Notification URL -->
              <v-alert type="info" variant="tonal" class="mb-4">
                <v-alert-title>URL de Notificação</v-alert-title>
                <div class="mt-2">
                  <code>{{ pagseguroNotificationUrl }}</code>
                  <v-btn
                    icon="mdi-content-copy"
                    size="small"
                    variant="text"
                    @click="copyToClipboard(pagseguroNotificationUrl)"
                    class="ml-2"
                  />
                </div>
              </v-alert>

              <!-- Payment Methods -->
              <v-expansion-panels variant="accordion">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    Métodos de Pagamento Habilitados
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <v-row>
                      <v-col cols="12" md="4">
                        <v-checkbox
                          v-model="pagseguroConfig.methods.credit_card"
                          label="Cartão de Crédito"
                          color="warning"
                        />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-checkbox
                          v-model="pagseguroConfig.methods.debit_card"
                          label="Cartão de Débito"
                          color="warning"
                        />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-checkbox
                          v-model="pagseguroConfig.methods.pix"
                          label="PIX"
                          color="warning"
                        />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-checkbox
                          v-model="pagseguroConfig.methods.boleto"
                          label="Boleto"
                          color="warning"
                        />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-checkbox
                          v-model="pagseguroConfig.methods.transfer"
                          label="Transferência"
                          color="warning"
                        />
                      </v-col>
                    </v-row>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </v-form>
        </v-card>
      </v-col>
    </v-row>

    <!-- General Settings -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card class="pa-6" elevation="2">
          <h3 class="text-h6 font-weight-bold mb-4">Configurações Gerais</h3>
          
          <v-row>
            <v-col cols="12" md="6">
              <v-select
                v-model="generalConfig.default_currency"
                :items="currencyOptions"
                label="Moeda Padrão"
                variant="outlined"
                class="mb-4"
              />

              <v-select
                v-model="generalConfig.billing_cycle"
                :items="billingCycleOptions"
                label="Ciclo de Cobrança Padrão"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="generalConfig.trial_days"
                label="Dias de Trial Gratuito"
                variant="outlined"
                type="number"
                class="mb-4"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-switch
                v-model="generalConfig.auto_invoice"
                label="Gerar Faturas Automaticamente"
                color="primary"
                inset
                class="mb-4"
              />

              <v-switch
                v-model="generalConfig.dunning_emails"
                label="Emails de Cobrança Automática"
                color="primary"
                inset
                class="mb-4"
              />

              <v-switch
                v-model="generalConfig.proration"
                label="Cobrança Proporcional"
                color="primary"
                inset
                class="mb-4"
              />
            </v-col>
          </v-row>

          <!-- Tax Settings -->
          <v-divider class="my-4" />
          <h4 class="text-h6 mb-4">Configurações de Impostos</h4>
          
          <v-row>
            <v-col cols="12" md="6">
              <v-switch
                v-model="taxConfig.calculate_tax"
                label="Calcular Impostos Automaticamente"
                color="primary"
                inset
                class="mb-4"
              />

              <v-text-field
                v-model="taxConfig.default_tax_rate"
                label="Taxa de Imposto Padrão (%)"
                variant="outlined"
                type="number"
                step="0.01"
                :disabled="!taxConfig.calculate_tax"
                class="mb-4"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="taxConfig.tax_id"
                label="CNPJ da Empresa"
                variant="outlined"
                class="mb-4"
              />

              <v-text-field
                v-model="taxConfig.company_name"
                label="Razão Social"
                variant="outlined"
                class="mb-4"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!-- Connection Status -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>Status das Conexões</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <template #prepend>
                  <v-icon 
                    :icon="connectionStatus.stripe.connected ? 'mdi-check-circle' : 'mdi-alert-circle'"
                    :color="connectionStatus.stripe.connected ? 'success' : 'error'"
                  />
                </template>
                <v-list-item-title>Stripe</v-list-item-title>
                <v-list-item-subtitle>
                  {{ connectionStatus.stripe.connected ? 'Conectado' : 'Desconectado' }}
                  <span v-if="connectionStatus.stripe.last_test" class="ml-2">
                    (Último teste: {{ formatDate(connectionStatus.stripe.last_test) }})
                  </span>
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template #prepend>
                  <v-icon 
                    :icon="connectionStatus.pagseguro.connected ? 'mdi-check-circle' : 'mdi-alert-circle'"
                    :color="connectionStatus.pagseguro.connected ? 'success' : 'error'"
                  />
                </template>
                <v-list-item-title>PagSeguro</v-list-item-title>
                <v-list-item-subtitle>
                  {{ connectionStatus.pagseguro.connected ? 'Conectado' : 'Desconectado' }}
                  <span v-if="connectionStatus.pagseguro.last_test" class="ml-2">
                    (Último teste: {{ formatDate(connectionStatus.pagseguro.last_test) }})
                  </span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Props
interface Props {
  saving?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  saving: false
})

// Emits
const emit = defineEmits(['save-settings'])

// Reactive data
const showStripeKeys = ref(false)
const showPagSeguroKeys = ref(false)
const testingStripe = ref(false)
const testingPagSeguro = ref(false)

// Configuration objects
const stripeConfig = ref({
  enabled: true,
  environment: 'sandbox',
  publishable_key: '',
  secret_key: '',
  webhook_secret: ''
})

const pagseguroConfig = ref({
  enabled: true,
  environment: 'sandbox',
  app_id: '',
  app_key: '',
  token: '',
  methods: {
    credit_card: true,
    debit_card: true,
    pix: true,
    boleto: true,
    transfer: false
  }
})

const generalConfig = ref({
  default_currency: 'BRL',
  billing_cycle: 'monthly',
  trial_days: 7,
  auto_invoice: true,
  dunning_emails: true,
  proration: true
})

const taxConfig = ref({
  calculate_tax: false,
  default_tax_rate: 0,
  tax_id: '',
  company_name: ''
})

const connectionStatus = ref({
  stripe: {
    connected: false,
    last_test: null
  },
  pagseguro: {
    connected: false,
    last_test: null
  }
})

// Options
const environmentOptions = [
  { title: 'Sandbox (Teste)', value: 'sandbox' },
  { title: 'Produção', value: 'production' }
]

const currencyOptions = [
  { title: 'Real Brasileiro (BRL)', value: 'BRL' },
  { title: 'Dólar Americano (USD)', value: 'USD' },
  { title: 'Euro (EUR)', value: 'EUR' }
]

const billingCycleOptions = [
  { title: 'Mensal', value: 'monthly' },
  { title: 'Anual', value: 'yearly' },
  { title: 'Trimestral', value: 'quarterly' }
]

// Computed URLs
const stripeWebhookUrl = ref('https://api.markfoot.com/webhooks/stripe')
const pagseguroNotificationUrl = ref('https://api.markfoot.com/webhooks/pagseguro')

// Webhook events
const stripeWebhookEvents = ref([
  'invoice.payment_succeeded',
  'invoice.payment_failed',
  'customer.subscription.created',
  'customer.subscription.updated',
  'customer.subscription.deleted'
])

// Methods
const testStripeConnection = async () => {
  testingStripe.value = true
  try {
    // Test Stripe connection
    console.log('Testing Stripe connection...')
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    connectionStatus.value.stripe.connected = true
    connectionStatus.value.stripe.last_test = new Date().toISOString()
  } catch (error) {
    console.error('Stripe connection failed:', error)
    connectionStatus.value.stripe.connected = false
  } finally {
    testingStripe.value = false
  }
}

const testPagSeguroConnection = async () => {
  testingPagSeguro.value = true
  try {
    // Test PagSeguro connection
    console.log('Testing PagSeguro connection...')
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    connectionStatus.value.pagseguro.connected = true
    connectionStatus.value.pagseguro.last_test = new Date().toISOString()
  } catch (error) {
    console.error('PagSeguro connection failed:', error)
    connectionStatus.value.pagseguro.connected = false
  } finally {
    testingPagSeguro.value = false
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    console.log('URL copiada para a área de transferência')
  } catch (error) {
    console.error('Erro ao copiar URL:', error)
  }
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

// Lifecycle
onMounted(() => {
  // Load current settings
  console.log('Loading financial settings...')
})
</script>

<style scoped>
.configuracoes-financeiras {
  width: 100%;
}

.stripe-logo,
.pagseguro-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background-color: rgba(var(--v-theme-surface), 0.1);
}

code {
  background-color: rgba(var(--v-theme-surface), 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.875rem;
}
</style>
