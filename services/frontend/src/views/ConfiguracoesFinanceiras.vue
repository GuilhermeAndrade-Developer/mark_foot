<template>
  <div class="configuracoes-financeiras">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Configurações Financeiras</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Configure as definições do sistema financeiro
        </p>
      </div>
      
      <!-- Actions -->
      <div class="d-flex ga-2">
        <v-btn color="primary" prepend-icon="mdi-content-save" @click="saveSettings" :loading="saving">
          Salvar Configurações
        </v-btn>
      </div>
    </div>

    <!-- Configurações Content -->
    <ConfiguracoesFinanceiras 
      @save-settings="saveSettings"
      :saving="saving"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ConfiguracoesFinanceiras from '@/components/financeiro/ConfiguracoesFinanceiras.vue'

// Reactive data
const saving = ref(false)

// Methods para Configurações
const saveSettings = async () => {
  saving.value = true
  try {
    console.log('Salvando configurações financeiras...')
    // Lógica de save aqui
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.configuracoes-financeiras {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
