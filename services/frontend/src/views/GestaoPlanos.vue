<template>
  <div class="gestao-planos">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Gestão de Planos</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerenciar planos de assinatura e preços
        </p>
      </div>
      
      <!-- Actions -->
      <div class="d-flex ga-2">
        <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreatePlanDialog">
          Novo Plano
        </v-btn>
      </div>
    </div>

    <!-- Planos Content -->
    <GestaoPlanos 
      @create-plan="showCreatePlanDialog"
    />
  </div>
</template>

<script setup lang="ts">
import GestaoPlanos from '@/components/financeiro/GestaoPlanos.vue'

// Methods para Planos
const showCreatePlanDialog = () => {
  console.log('Abrindo dialog de criação de plano...')
}
</script>

<style scoped>
.gestao-planos {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
