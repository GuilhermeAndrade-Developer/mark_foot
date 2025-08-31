<template>
  <div class="gestao-clientes">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Gestão de Clientes</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerenciar clientes e prospectos da plataforma
        </p>
      </div>
      
      <!-- Actions -->
      <div class="d-flex ga-2">
        <v-btn color="primary" prepend-icon="mdi-account-plus" @click="addNewClient">
          Novo Cliente
        </v-btn>
        <v-btn color="secondary" prepend-icon="mdi-account-search" @click="searchClients">
          Buscar Clientes
        </v-btn>
      </div>
    </div>

    <!-- Tabs para alternar entre Novos Clientes e Buscar Clientes -->
    <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="mb-6">
      <v-tab value="new-clients" prepend-icon="mdi-account-plus">
        Novos Clientes
      </v-tab>
      <v-tab value="search-clients" prepend-icon="mdi-account-search">
        Buscar Clientes
      </v-tab>
    </v-tabs>

    <!-- Content das Tabs -->
    <v-tabs-window v-model="activeTab">
      <!-- Tab Novos Clientes -->
      <v-tabs-window-item value="new-clients">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-account-plus</v-icon>
            Novos Clientes
          </v-card-title>
          <v-card-text>
            <v-row>
              <!-- Formulário para adicionar novo cliente -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newClient.name"
                  label="Nome Completo"
                  prepend-inner-icon="mdi-account"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newClient.email"
                  label="E-mail"
                  type="email"
                  prepend-inner-icon="mdi-email"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newClient.phone"
                  label="Telefone"
                  prepend-inner-icon="mdi-phone"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newClient.plan"
                  :items="availablePlans"
                  label="Plano"
                  prepend-inner-icon="mdi-package-variant"
                  outlined
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="newClient.notes"
                  label="Observações"
                  prepend-inner-icon="mdi-note-text"
                  outlined
                  rows="3"
                />
              </v-col>
              <v-col cols="12">
                <v-btn color="primary" @click="saveNewClient" :loading="saving">
                  <v-icon class="mr-2">mdi-content-save</v-icon>
                  Salvar Cliente
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- Tab Buscar Clientes -->
      <v-tabs-window-item value="search-clients">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-account-search</v-icon>
            Buscar Clientes
          </v-card-title>
          <v-card-text>
            <!-- Filtros de busca -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchFilters.name"
                  label="Nome"
                  prepend-inner-icon="mdi-account"
                  outlined
                  clearable
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchFilters.email"
                  label="E-mail"
                  prepend-inner-icon="mdi-email"
                  outlined
                  clearable
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="searchFilters.plan"
                  :items="availablePlans"
                  label="Plano"
                  prepend-inner-icon="mdi-package-variant"
                  outlined
                  clearable
                />
              </v-col>
            </v-row>

            <!-- Botões de ação -->
            <div class="d-flex ga-2 mb-4">
              <v-btn color="primary" @click="searchClientsAction" :loading="searching">
                <v-icon class="mr-2">mdi-magnify</v-icon>
                Buscar
              </v-btn>
              <v-btn variant="outlined" @click="clearFilters">
                <v-icon class="mr-2">mdi-filter-remove</v-icon>
                Limpar Filtros
              </v-btn>
            </div>

            <!-- Tabela de resultados -->
            <v-data-table
              :headers="clientHeaders"
              :items="clients"
              :loading="searching"
              class="elevation-1"
            >
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  color="primary"
                  variant="text"
                  @click="editClient(item)"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  variant="text"
                  @click="deleteClient(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// Reactive data
const activeTab = ref('new-clients')
const saving = ref(false)
const searching = ref(false)

// Dados do novo cliente
const newClient = reactive({
  name: '',
  email: '',
  phone: '',
  plan: '',
  notes: ''
})

// Filtros de busca
const searchFilters = reactive({
  name: '',
  email: '',
  plan: ''
})

// Dados mock
const availablePlans = ['Básico', 'Premium', 'Enterprise']

const clients = ref([
  {
    id: 1,
    name: 'João Silva',
    email: 'joao@email.com',
    phone: '(11) 99999-9999',
    plan: 'Premium',
    created_at: '2024-01-15'
  },
  {
    id: 2,
    name: 'Maria Santos',
    email: 'maria@email.com',
    phone: '(11) 88888-8888',
    plan: 'Básico',
    created_at: '2024-01-20'
  }
])

const clientHeaders = [
  { title: 'ID', key: 'id' },
  { title: 'Nome', key: 'name' },
  { title: 'E-mail', key: 'email' },
  { title: 'Telefone', key: 'phone' },
  { title: 'Plano', key: 'plan' },
  { title: 'Data Cadastro', key: 'created_at' },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Methods
const addNewClient = () => {
  activeTab.value = 'new-clients'
}

const searchClients = () => {
  activeTab.value = 'search-clients'
}

const saveNewClient = async () => {
  saving.value = true
  try {
    console.log('Salvando novo cliente:', newClient)
    // Aqui seria feita a chamada para a API
    
    // Reset form
    Object.assign(newClient, {
      name: '',
      email: '',
      phone: '',
      plan: '',
      notes: ''
    })
  } finally {
    saving.value = false
  }
}

const searchClientsAction = async () => {
  searching.value = true
  try {
    console.log('Buscando clientes com filtros:', searchFilters)
    // Aqui seria feita a chamada para a API
  } finally {
    searching.value = false
  }
}

const clearFilters = () => {
  Object.assign(searchFilters, {
    name: '',
    email: '',
    plan: ''
  })
}

const editClient = (client: any) => {
  console.log('Editando cliente:', client)
}

const deleteClient = (client: any) => {
  console.log('Deletando cliente:', client)
}
</script>

<style scoped>
.gestao-clientes {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.v-tabs >>> .v-tab {
  text-transform: none;
  font-weight: 500;
}
</style>
