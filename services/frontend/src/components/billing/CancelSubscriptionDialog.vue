<template>
  <v-dialog
    v-model="dialog"
    max-width="500"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon icon="mdi-alert" color="warning" class="mr-2" />
        <span class="text-h6 font-weight-bold">Cancelar Assinatura</span>
      </v-card-title>

      <v-card-text class="pa-6">
        <div v-if="subscription">
          <v-alert
            type="warning"
            variant="tonal"
            class="mb-4"
          >
            <template #title>Atenção</template>
            <div>
              Você está prestes a cancelar sua assinatura do plano 
              <strong>{{ subscription.plan.name }}</strong>.
            </div>
          </v-alert>

          <div class="mb-4">
            <h4 class="text-subtitle-1 font-weight-bold mb-2">
              O que acontecerá após o cancelamento:
            </h4>
            <ul class="text-body-2 ml-4">
              <li class="mb-1">
                Sua assinatura permanecerá ativa até 
                <strong>{{ formatDate(subscription.expires_at) }}</strong>
              </li>
              <li class="mb-1">
                Após essa data, você será automaticamente movido para o plano Free
              </li>
              <li class="mb-1">
                Você perderá acesso às funcionalidades premium
              </li>
              <li class="mb-1">
                Seu limite de API será reduzido para 100 calls/mês
              </li>
              <li class="mb-1">
                Não haverá mais cobranças automáticas
              </li>
            </ul>
          </div>

          <div class="mb-4">
            <h4 class="text-subtitle-1 font-weight-bold mb-2">
              Recursos que você perderá:
            </h4>
            <div class="d-flex flex-wrap ga-2">
              <v-chip
                v-for="feature in lostFeatures"
                :key="feature"
                variant="outlined"
                color="error"
                size="small"
              >
                {{ feature }}
              </v-chip>
            </div>
          </div>

          <v-textarea
            v-model="cancelReason"
            label="Motivo do cancelamento (opcional)"
            placeholder="Nos ajude a melhorar. Por que você está cancelando?"
            rows="3"
            variant="outlined"
            hide-details
          />

          <v-alert
            v-if="subscription.billing_cycle === 'yearly'"
            type="info"
            variant="tonal"
            class="mt-4"
          >
            <template #title>Reembolso</template>
            <div>
              Como você tem um plano anual, entre em contato com nosso suporte 
              para discutir opções de reembolso proporcional.
            </div>
          </v-alert>
        </div>
      </v-card-text>

      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="$emit('update:modelValue', false)"
          :disabled="cancelling"
        >
          Manter Assinatura
        </v-btn>
        <v-btn
          color="error"
          @click="confirmCancel"
          :loading="cancelling"
          :disabled="!subscription"
        >
          Confirmar Cancelamento
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Feedback Dialog -->
    <v-dialog
      v-model="showFeedbackDialog"
      max-width="400"
      persistent
    >
      <v-card>
        <v-card-title class="text-center">
          <v-icon icon="mdi-heart-broken" color="error" size="48" class="mb-2" />
          <div class="text-h6">Que pena!</div>
        </v-card-title>

        <v-card-text class="text-center pa-6">
          <p class="text-body-1 mb-4">
            Sua assinatura foi cancelada com sucesso.
          </p>
          <p class="text-body-2 text-medium-emphasis">
            Você ainda tem acesso às funcionalidades premium até 
            <strong>{{ subscription ? formatDate(subscription.expires_at) : '' }}</strong>.
          </p>
          <p class="text-body-2 text-medium-emphasis mt-2">
            Esperamos vê-lo(a) de volta em breve! 💙
          </p>
        </v-card-text>

        <v-card-actions class="justify-center pa-6 pt-0">
          <v-btn
            color="primary"
            variant="outlined"
            @click="closeFeedback"
          >
            Entendido
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { billingApi, type UserSubscription } from '@/services/billingApi'

// Props
interface Props {
  modelValue: boolean
  subscription?: UserSubscription
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'cancelled': [subscription: UserSubscription]
}>()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const cancelling = ref(false)
const cancelReason = ref('')
const showFeedbackDialog = ref(false)

// Computed
const lostFeatures = computed(() => {
  if (!props.subscription) return []
  
  const features: string[] = []
  
  if (props.subscription.plan.advanced_ai_analysis) {
    features.push('Análises avançadas de IA')
  }
  
  if (props.subscription.plan.unlimited_reports) {
    features.push('Relatórios ilimitados')
  }
  
  if (props.subscription.plan.white_label) {
    features.push('White-label')
  }
  
  if (props.subscription.plan.dedicated_support) {
    features.push('Suporte dedicado')
  }
  
  if (props.subscription.plan.multi_tenancy) {
    features.push('Multi-tenancy')
  }
  
  // Add API limit difference
  const currentLimit = props.subscription.plan.api_calls_limit
  if (currentLimit > 100) {
    features.push(`${(currentLimit - 100).toLocaleString()} API calls extras`)
  }
  
  return features
})

// Methods
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const confirmCancel = async () => {
  if (!props.subscription) return
  
  cancelling.value = true
  
  try {
    const cancelledSubscription = await billingApi.cancelSubscription(
      props.subscription.id,
      cancelReason.value || 'Cancelado via dashboard'
    )
    
    emit('cancelled', cancelledSubscription)
    dialog.value = false
    showFeedbackDialog.value = true
  } catch (error) {
    console.error('Error cancelling subscription:', error)
    // TODO: Show error message
  } finally {
    cancelling.value = false
  }
}

const closeFeedback = () => {
  showFeedbackDialog.value = false
  cancelReason.value = ''
}
</script>

<style scoped>
.v-alert >>> .v-alert__content {
  line-height: 1.5;
}

ul {
  list-style-type: disc;
}

li {
  line-height: 1.6;
}
</style>
