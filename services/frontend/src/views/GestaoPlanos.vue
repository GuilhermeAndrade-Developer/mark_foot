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
      ref="gestaoPlanos"
      @create-plan="showCreatePlanDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import GestaoPlanos from '@/components/financeiro/GestaoPlanos.vue'

// Referência ao componente filho
const gestaoPlanos = ref()

// Methods para Planos
const showCreatePlanDialog = () => {
  // Chamar método do componente filho para abrir o modal
  if (gestaoPlanos.value) {
    gestaoPlanos.value.openCreateDialog()
  }
}
</script>

<style scoped>
.gestao-planos {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
