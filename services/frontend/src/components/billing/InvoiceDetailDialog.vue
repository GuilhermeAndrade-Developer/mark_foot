<template>
  <v-dialog
    v-model="dialog"
    max-width="600"
    scrollable
  >
    <v-card v-if="invoice">
      <v-card-title class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon icon="mdi-receipt-text" class="mr-2" />
          <span class="text-h6 font-weight-bold">
            Fatura #{{ invoice.invoice_number }}
          </span>
        </div>
        <v-chip
          :color="getStatusColor(invoice.status)"
          :variant="invoice.status === 'paid' ? 'flat' : 'tonal'"
          size="small"
        >
          <v-icon 
            :icon="getStatusIcon(invoice.status)" 
            start
            size="16"
          />
          {{ getStatusText(invoice.status) }}
        </v-chip>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-0">
        <!-- Header Information -->
        <div class="pa-6 pb-4">
          <v-row>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">Data de Emissão</div>
              <div class="text-body-1 font-weight-medium">
                {{ formatDate(invoice.created_at) }}
              </div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">Vencimento</div>
              <div class="text-body-1 font-weight-medium">
                {{ formatDate(invoice.due_date) }}
              </div>
            </v-col>
          </v-row>

          <v-row v-if="invoice.paid_at" class="mt-2">
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">Data de Pagamento</div>
              <div class="text-body-1 font-weight-medium">
                {{ formatDate(invoice.paid_at) }}
              </div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">Método de Pagamento</div>
              <div class="text-body-1 font-weight-medium">
                {{ getPaymentMethodText(invoice.payment_method) }}
              </div>
            </v-col>
          </v-row>
        </div>

        <v-divider />

        <!-- Subscription Information -->
        <div class="pa-6 py-4">
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Informações da Assinatura
          </div>
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-icon 
                :icon="getPlanIcon(invoice.subscription.plan.name)" 
                :color="getPlanColor(invoice.subscription.plan.name)"
              />
            </v-avatar>
            <div>
              <div class="text-body-1 font-weight-medium">
                {{ invoice.subscription.plan.name }}
              </div>
              <div class="text-body-2 text-medium-emphasis">
                {{ getBillingPeriodText(invoice.subscription.billing_cycle) }}
              </div>
            </div>
          </div>
        </div>

        <v-divider />

        <!-- Invoice Items -->
        <div class="pa-6 py-4">
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Itens da Fatura
          </div>
          
          <v-table density="compact">
            <thead>
              <tr>
                <th class="text-left">Descrição</th>
                <th class="text-center">Período</th>
                <th class="text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="font-weight-medium">
                    Assinatura {{ invoice.subscription.plan.name }}
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    {{ invoice.subscription.plan.description }}
                  </div>
                </td>
                <td class="text-center">
                  <div class="text-body-2">
                    {{ formatPeriod() }}
                  </div>
                </td>
                <td class="text-right font-weight-medium">
                  {{ formatCurrency(invoice.amount) }}
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>

        <v-divider />

        <!-- Total -->
        <div class="pa-6 py-4">
          <v-row align="center">
            <v-col>
              <div class="text-h6 font-weight-bold">Total</div>
            </v-col>
            <v-col cols="auto">
              <div class="text-h5 font-weight-bold text-primary">
                {{ formatCurrency(invoice.amount) }}
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Notes -->
        <div v-if="invoice.notes" class="pa-6 pt-0">
          <v-divider class="mb-4" />
          <div class="text-subtitle-2 font-weight-bold mb-2">
            Observações
          </div>
          <div class="text-body-2">
            {{ invoice.notes }}
          </div>
        </div>

        <!-- Payment Actions -->
        <div v-if="invoice.status === 'pending'" class="pa-6 pt-0">
          <v-divider class="mb-4" />
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <template #title>Pagamento Pendente</template>
            <div>
              Esta fatura ainda não foi paga. O vencimento é em 
              <strong>{{ formatDate(invoice.due_date) }}</strong>.
            </div>
          </v-alert>

          <div class="d-flex ga-2">
            <v-btn
              color="primary"
              variant="flat"
              @click="processPayment"
              :loading="processing"
            >
              <v-icon icon="mdi-credit-card" start />
              Pagar Agora
            </v-btn>
            <v-btn
              variant="outlined"
              @click="downloadPdf"
              :loading="downloading"
            >
              <v-icon icon="mdi-download" start />
              Baixar PDF
            </v-btn>
          </div>
        </div>

        <!-- Payment Success Actions -->
        <div v-else-if="invoice.status === 'paid'" class="pa-6 pt-0">
          <v-divider class="mb-4" />
          <v-alert
            type="success"
            variant="tonal"
            class="mb-4"
          >
            <template #title>Pagamento Confirmado</template>
            <div>
              Esta fatura foi paga em 
              <strong>{{ formatDate(invoice.paid_at!) }}</strong>.
            </div>
          </v-alert>

          <div class="d-flex ga-2">
            <v-btn
              variant="outlined"
              @click="downloadPdf"
              :loading="downloading"
            >
              <v-icon icon="mdi-download" start />
              Baixar PDF
            </v-btn>
            <v-btn
              variant="outlined"
              @click="downloadReceipt"
              :loading="downloadingReceipt"
            >
              <v-icon icon="mdi-receipt" start />
              Baixar Comprovante
            </v-btn>
          </div>
        </div>

        <!-- Overdue Actions -->
        <div v-else-if="invoice.status === 'overdue'" class="pa-6 pt-0">
          <v-divider class="mb-4" />
          <v-alert
            type="error"
            variant="tonal"
            class="mb-4"
          >
            <template #title>Fatura Vencida</template>
            <div>
              Esta fatura venceu em <strong>{{ formatDate(invoice.due_date) }}</strong>.
              Pague o quanto antes para evitar a suspensão do serviço.
            </div>
          </v-alert>

          <div class="d-flex ga-2">
            <v-btn
              color="error"
              variant="flat"
              @click="processPayment"
              :loading="processing"
            >
              <v-icon icon="mdi-credit-card" start />
              Pagar Agora
            </v-btn>
            <v-btn
              variant="outlined"
              @click="downloadPdf"
              :loading="downloading"
            >
              <v-icon icon="mdi-download" start />
              Baixar PDF
            </v-btn>
          </div>
        </div>
      </v-card-text>

      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="$emit('update:modelValue', false)"
        >
          Fechar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { billingApi, type Invoice } from '@/services/billingApi'

// Props
interface Props {
  modelValue: boolean
  invoice?: Invoice
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'paid': [invoice: Invoice]
}>()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const processing = ref(false)
const downloading = ref(false)
const downloadingReceipt = ref(false)

// Methods
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(amount)
}

const formatPeriod = () => {
  if (!props.invoice) return ''
  
  const startDate = new Date(props.invoice.created_at)
  const endDate = new Date(startDate)
  
  if (props.invoice.subscription.billing_cycle === 'monthly') {
    endDate.setMonth(endDate.getMonth() + 1)
  } else {
    endDate.setFullYear(endDate.getFullYear() + 1)
  }
  
  return `${startDate.toLocaleDateString('pt-BR')} - ${endDate.toLocaleDateString('pt-BR')}`
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'paid': return 'success'
    case 'pending': return 'warning'
    case 'overdue': return 'error'
    case 'cancelled': return 'default'
    default: return 'default'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'paid': return 'mdi-check-circle'
    case 'pending': return 'mdi-clock-outline'
    case 'overdue': return 'mdi-alert-circle'
    case 'cancelled': return 'mdi-cancel'
    default: return 'mdi-help-circle'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'paid': return 'Pago'
    case 'pending': return 'Pendente'
    case 'overdue': return 'Vencido'
    case 'cancelled': return 'Cancelado'
    default: return 'Desconhecido'
  }
}

const getPaymentMethodText = (method?: string) => {
  if (!method) return 'N/A'
  
  switch (method) {
    case 'credit_card': return 'Cartão de Crédito'
    case 'debit_card': return 'Cartão de Débito'
    case 'bank_transfer': return 'Transferência Bancária'
    case 'pix': return 'PIX'
    case 'boleto': return 'Boleto Bancário'
    default: return method
  }
}

const getPlanIcon = (planName: string) => {
  switch (planName.toLowerCase()) {
    case 'free': return 'mdi-heart-outline'
    case 'premium': return 'mdi-star'
    case 'enterprise': return 'mdi-office-building'
    default: return 'mdi-package-variant'
  }
}

const getPlanColor = (planName: string) => {
  switch (planName.toLowerCase()) {
    case 'free': return 'grey'
    case 'premium': return 'primary'
    case 'enterprise': return 'purple'
    default: return 'grey'
  }
}

const getBillingPeriodText = (cycle: string) => {
  switch (cycle) {
    case 'monthly': return 'Mensal'
    case 'yearly': return 'Anual'
    default: return cycle
  }
}

const processPayment = async () => {
  if (!props.invoice) return
  
  processing.value = true
  
  try {
    const paidInvoice = await billingApi.payInvoice(props.invoice.id)
    emit('paid', paidInvoice)
    // TODO: Show success message
  } catch (error) {
    console.error('Error processing payment:', error)
    // TODO: Show error message
  } finally {
    processing.value = false
  }
}

const downloadPdf = async () => {
  if (!props.invoice) return
  
  downloading.value = true
  
  try {
    const blob = await billingApi.downloadInvoice(props.invoice.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `fatura-${props.invoice.invoice_number}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading PDF:', error)
    // TODO: Show error message
  } finally {
    downloading.value = false
  }
}

const downloadReceipt = async () => {
  if (!props.invoice) return
  
  downloadingReceipt.value = true
  
  try {
    const blob = await billingApi.downloadReceipt(props.invoice.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `comprovante-${props.invoice.invoice_number}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading receipt:', error)
    // TODO: Show error message
  } finally {
    downloadingReceipt.value = false
  }
}
</script>

<style scoped>
.v-table >>> th {
  font-weight: 600 !important;
  font-size: 0.875rem !important;
}

.v-table >>> td {
  padding: 8px 16px !important;
}

.v-alert >>> .v-alert__content {
  line-height: 1.5;
}
</style>
