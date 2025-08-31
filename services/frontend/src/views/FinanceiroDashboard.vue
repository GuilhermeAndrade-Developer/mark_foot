<template>
  <div class="financeiro-dashboard">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Dashboard Financeiro</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Visão geral dos dados financeiros da plataforma
        </p>
      </div>
      
      <!-- Actions -->
      <div class="d-flex ga-2">
        <v-btn color="success" prepend-icon="mdi-download" @click="exportReport">
          Exportar Relatório
        </v-btn>
        <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshData">
          Atualizar
        </v-btn>
      </div>
    </div>

    <!-- Dashboard Content -->
    <DashboardFinanceiro 
      @export-report="exportReport"
      @refresh-data="refreshData"
    />
  </div>
</template>

<script setup lang="ts">
import DashboardFinanceiro from '@/components/financeiro/DashboardFinanceiro.vue'

// Methods para Dashboard
const exportReport = () => {
  console.log('Exportando relatório financeiro...')
}

const refreshData = () => {
  console.log('Atualizando dados financeiros...')
}
</script>

<style scoped>
.financeiro-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
