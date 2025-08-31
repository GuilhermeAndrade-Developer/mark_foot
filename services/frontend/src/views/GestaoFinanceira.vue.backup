<template>
  <div class="gestao-financeira">
    <!-- Header principal com navegação entre as views -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Gestão Financeira</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Sistema completo de administração financeira da plataforma
        </p>
      </div>
      
      <!-- Actions específicas por view -->
      <div class="d-flex ga-2">
        <!-- Dashboard actions -->
        <template v-if="activeView === 'dashboard'">
          <v-btn color="success" prepend-icon="mdi-download" @click="exportReport">
            Exportar Relatório
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshData">
            Atualizar
          </v-btn>
        </template>
        
        <!-- Configurações actions -->
        <template v-if="activeView === 'configuracoes'">
          <v-btn color="primary" prepend-icon="mdi-content-save" @click="saveSettings" :loading="saving">
            Salvar Configurações
          </v-btn>
        </template>
        
        <!-- Planos actions -->
        <template v-if="activeView === 'planos'">
          <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreatePlanDialog">
            Novo Plano
          </v-btn>
        </template>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <v-tabs 
      v-model="activeView" 
      bg-color="transparent" 
      color="primary"
      class="mb-6"
    >
      <v-tab value="dashboard" prepend-icon="mdi-chart-line">
        Dashboard
      </v-tab>
      <v-tab value="configuracoes" prepend-icon="mdi-cog">
        Configurações
      </v-tab>
      <v-tab value="planos" prepend-icon="mdi-package-variant">
        Gestão de Planos
      </v-tab>
    </v-tabs>

    <!-- View Content -->
    <v-tabs-window v-model="activeView">
      <!-- Dashboard Tab -->
      <v-tabs-window-item value="dashboard">
        <DashboardFinanceiro 
          @export-report="exportReport"
          @refresh-data="refreshData"
        />
      </v-tabs-window-item>

      <!-- Configurações Tab -->
      <v-tabs-window-item value="configuracoes">
        <ConfiguracoesFinanceiras 
          @save-settings="saveSettings"
          :saving="saving"
        />
      </v-tabs-window-item>

      <!-- Planos Tab -->
      <v-tabs-window-item value="planos">
        <GestaoPlanos 
          @create-plan="showCreatePlanDialog"
        />
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DashboardFinanceiro from '@/components/financeiro/DashboardFinanceiro.vue'
import ConfiguracoesFinanceiras from '@/components/financeiro/ConfiguracoesFinanceiras.vue'
import GestaoPlanos from '@/components/financeiro/GestaoPlanos.vue'

// Reactive data
const activeView = ref('dashboard')
const saving = ref(false)

// Methods para Dashboard
const exportReport = () => {
  console.log('Exportando relatório financeiro...')
}

const refreshData = () => {
  console.log('Atualizando dados financeiros...')
}

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

// Methods para Planos
const showCreatePlanDialog = () => {
  console.log('Abrindo dialog de criação de plano...')
}
</script>

<style scoped>
.gestao-financeira {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.v-tabs >>> .v-tab {
  text-transform: none;
  font-weight: 500;
}

.v-tabs-window {
  margin-top: 0;
}
</style>
