<template>
  <div class="forum-moderation">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Moderação do Fórum</h1>
        <p class="text-body-1 text-medium-emphasis">
          Gerencie denúncias, posts reportados e ações de moderação
        </p>
      </div>
      <v-btn
        color="primary"
        prepend-icon="mdi-cog"
        @click="settingsDialog = true"
      >
        Configurações
      </v-btn>
    </div>

    <!-- Quick Stats -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="warning" class="mr-3">
              <v-icon>mdi-flag</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ pendingReports }}</div>
              <div class="text-body-2 text-medium-emphasis">Denúncias Pendentes</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="error" class="mr-3">
              <v-icon>mdi-account-remove</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ bannedUsers }}</div>
              <div class="text-body-2 text-medium-emphasis">Usuários Banidos</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="success" class="mr-3">
              <v-icon>mdi-check-circle</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ resolvedToday }}</div>
              <div class="text-body-2 text-medium-emphasis">Resolvidas Hoje</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="info" class="mr-3">
              <v-icon>mdi-shield-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ moderators.length }}</div>
              <div class="text-body-2 text-medium-emphasis">Moderadores Ativos</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-6">
      <v-tab value="reports">
        <v-icon class="mr-2">mdi-flag</v-icon>
        Denúncias
        <v-chip
          v-if="pendingReports > 0"
          color="warning"
          size="x-small"
          class="ml-2"
        >
          {{ pendingReports }}
        </v-chip>
      </v-tab>
      <v-tab value="users">
        <v-icon class="mr-2">mdi-account-group</v-icon>
        Usuários
      </v-tab>
      <v-tab value="logs">
        <v-icon class="mr-2">mdi-history</v-icon>
        Log de Ações
      </v-tab>
      <v-tab value="moderators">
        <v-icon class="mr-2">mdi-shield-account</v-icon>
        Moderadores
      </v-tab>
    </v-tabs>

    <!-- Content -->
    <v-window v-model="activeTab">
      <!-- Reports Tab -->
      <v-window-item value="reports">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-flag</v-icon>
            Denúncias de Posts
            <v-spacer />
            <v-select
              v-model="reportFilter"
              :items="reportFilterOptions"
              label="Filtrar por status"
              density="compact"
              style="max-width: 200px;"
              @update:model-value="loadReports"
            />
          </v-card-title>
          
          <v-data-table
            :headers="reportHeaders"
            :items="reports"
            :loading="loading"
            item-key="id"
            class="elevation-0"
          >
            <!-- Reported Content -->
            <template #item.content="{ item }">
              <div class="py-2">
                <div class="text-body-2 font-weight-medium mb-1">{{ item.post_title }}</div>
                <div class="text-body-2 text-truncate" style="max-width: 300px;">
                  {{ item.post_content }}
                </div>
                <v-chip size="x-small" color="primary" variant="outlined" class="mt-1">
                  {{ item.category }}
                </v-chip>
              </div>
            </template>

            <!-- Reporter -->
            <template #item.reporter="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="24" class="mr-2">
                  <v-icon size="16">mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="text-body-2">{{ item.reporter_name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ formatDate(item.reported_at) }}</div>
                </div>
              </div>
            </template>

            <!-- Reason -->
            <template #item.reason="{ item }">
              <v-chip
                :color="getReasonColor(item.reason)"
                size="small"
                variant="flat"
              >
                {{ getReasonText(item.reason) }}
              </v-chip>
            </template>

            <!-- Status -->
            <template #item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="flat"
              >
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex align-center">
                <v-tooltip text="Ver Post">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-eye"
                      size="small"
                      variant="text"
                      @click="viewPost(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-menu v-if="item.status === 'pending'">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-gavel"
                      size="small"
                      variant="text"
                      color="primary"
                    />
                  </template>
                  <v-list>
                    <v-list-item @click="approveReport(item)">
                      <v-list-item-title>
                        <v-icon class="mr-2" color="success">mdi-check</v-icon>
                        Aprovar Denúncia
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="rejectReport(item)">
                      <v-list-item-title>
                        <v-icon class="mr-2" color="error">mdi-close</v-icon>
                        Rejeitar Denúncia
                      </v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item @click="deletePost(item)">
                      <v-list-item-title class="text-error">
                        <v-icon class="mr-2">mdi-delete</v-icon>
                        Excluir Post
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="banUser(item)">
                      <v-list-item-title class="text-error">
                        <v-icon class="mr-2">mdi-account-remove</v-icon>
                        Banir Usuário
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Users Tab -->
      <v-window-item value="users">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-group</v-icon>
            Usuários com Restrições
            <v-spacer />
            <v-text-field
              v-model="userSearch"
              label="Buscar usuário"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              style="max-width: 300px;"
              clearable
            />
          </v-card-title>
          
          <v-data-table
            :headers="userHeaders"
            :items="moderatedUsers"
            :loading="loading"
            item-key="id"
            class="elevation-0"
          >
            <!-- User Info -->
            <template #item.user="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-3">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="text-body-2 font-weight-medium">{{ item.name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
                </div>
              </div>
            </template>

            <!-- Restriction -->
            <template #item.restriction="{ item }">
              <v-chip
                :color="getRestrictionColor(item.restriction)"
                size="small"
                variant="flat"
              >
                {{ getRestrictionText(item.restriction) }}
              </v-chip>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex align-center">
                <v-tooltip text="Ver Histórico">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-history"
                      size="small"
                      variant="text"
                      @click="viewUserHistory(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Remover Restrição">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-account-check"
                      size="small"
                      variant="text"
                      color="success"
                      @click="removeRestriction(item)"
                    />
                  </template>
                </v-tooltip>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Logs Tab -->
      <v-window-item value="logs">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-history</v-icon>
            Log de Ações de Moderação
            <v-spacer />
            <v-select
              v-model="logFilter"
              :items="logFilterOptions"
              label="Filtrar por tipo"
              density="compact"
              style="max-width: 200px;"
            />
          </v-card-title>
          
          <v-data-table
            :headers="logHeaders"
            :items="moderationLogs"
            :loading="loading"
            item-key="id"
            class="elevation-0"
          >
            <!-- Action -->
            <template #item.action="{ item }">
              <v-chip
                :color="getActionColor(item.action)"
                size="small"
                variant="flat"
              >
                <v-icon start :icon="getActionIcon(item.action)" />
                {{ getActionText(item.action) }}
              </v-chip>
            </template>

            <!-- Moderator -->
            <template #item.moderator="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="24" class="mr-2">
                  <v-icon size="16">mdi-shield-account</v-icon>
                </v-avatar>
                <span class="text-body-2">{{ item.moderator_name }}</span>
              </div>
            </template>

            <!-- Target -->
            <template #item.target="{ item }">
              <div class="text-body-2">
                <div>{{ item.target_type }}: {{ item.target_title }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.target_user }}</div>
              </div>
            </template>

            <!-- Date -->
            <template #item.created_at="{ item }">
              <div class="text-body-2">{{ formatDate(item.created_at) }}</div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Moderators Tab -->
      <v-window-item value="moderators">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-shield-account</v-icon>
            Moderadores
            <v-spacer />
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="addModeratorDialog = true"
            >
              Adicionar Moderador
            </v-btn>
          </v-card-title>
          
          <v-data-table
            :headers="moderatorHeaders"
            :items="moderators"
            :loading="loading"
            item-key="id"
            class="elevation-0"
          >
            <!-- User Info -->
            <template #item.user="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-3">
                  <v-icon>mdi-shield-account</v-icon>
                </v-avatar>
                <div>
                  <div class="text-body-2 font-weight-medium">{{ item.name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
                </div>
              </div>
            </template>

            <!-- Permissions -->
            <template #item.permissions="{ item }">
              <div class="d-flex flex-wrap gap-1">
                <v-chip
                  v-for="permission in item.permissions"
                  :key="permission"
                  size="x-small"
                  color="primary"
                  variant="outlined"
                >
                  {{ permission }}
                </v-chip>
              </div>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex align-center">
                <v-tooltip text="Editar Permissões">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-pencil"
                      size="small"
                      variant="text"
                      @click="editModerator(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Remover Moderador">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="removeModerator(item)"
                    />
                  </template>
                </v-tooltip>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Settings Dialog -->
    <v-dialog v-model="settingsDialog" max-width="600">
      <v-card>
        <v-card-title>Configurações de Moderação</v-card-title>
        <v-card-text>
          <v-switch
            v-model="settings.autoModeration"
            label="Moderação Automática"
            color="primary"
            class="mb-3"
          />
          
          <v-switch
            v-model="settings.requireApproval"
            label="Aprovar Novos Posts"
            color="primary"
            class="mb-3"
          />
          
          <v-text-field
            v-model="settings.maxReportsBeforeHide"
            label="Máximo de denúncias antes de ocultar"
            type="number"
            density="compact"
            class="mb-3"
          />
          
          <v-textarea
            v-model="settings.bannedWords"
            label="Palavras Banidas (uma por linha)"
            rows="4"
            density="compact"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="settingsDialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveSettings">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// State
const loading = ref(false)
const activeTab = ref('reports')
const settingsDialog = ref(false)
const addModeratorDialog = ref(false)

// Filters
const reportFilter = ref('pending')
const userSearch = ref('')
const logFilter = ref('all')

// Settings
const settings = ref({
  autoModeration: true,
  requireApproval: false,
  maxReportsBeforeHide: 5,
  bannedWords: 'spam\nfake\nscam'
})

// Mock data
const pendingReports = ref(12)
const bannedUsers = ref(3)
const resolvedToday = ref(8)

const reports = ref([
  {
    id: 1,
    post_title: 'Análise do último jogo',
    post_content: 'Este post contém linguagem inadequada...',
    category: 'Bayern München',
    reporter_name: 'João Silva',
    reported_at: new Date().toISOString(),
    reason: 'inappropriate',
    status: 'pending'
  }
])

const moderatedUsers = ref([
  {
    id: 1,
    name: 'Carlos Santos',
    email: 'carlos@email.com',
    restriction: 'banned',
    restricted_at: new Date().toISOString(),
    reason: 'Spam repetido'
  }
])

const moderationLogs = ref([
  {
    id: 1,
    action: 'ban_user',
    moderator_name: 'Admin',
    target_type: 'Usuário',
    target_title: 'Carlos Santos',
    target_user: 'carlos@email.com',
    created_at: new Date().toISOString()
  }
])

const moderators = ref([
  {
    id: 1,
    name: 'Admin Principal',
    email: 'admin@markfoot.com',
    permissions: ['delete_posts', 'ban_users', 'manage_categories'],
    added_at: new Date().toISOString()
  }
])

// Options
const reportFilterOptions = [
  { title: 'Pendentes', value: 'pending' },
  { title: 'Aprovadas', value: 'approved' },
  { title: 'Rejeitadas', value: 'rejected' },
  { title: 'Todas', value: 'all' }
]

const logFilterOptions = [
  { title: 'Todas', value: 'all' },
  { title: 'Banimentos', value: 'ban' },
  { title: 'Exclusões', value: 'delete' },
  { title: 'Moderação', value: 'moderate' }
]

// Table headers
const reportHeaders = [
  { title: 'Conteúdo Reportado', key: 'content', sortable: false },
  { title: 'Denunciante', key: 'reporter', sortable: false },
  { title: 'Motivo', key: 'reason', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

const userHeaders = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Restrição', key: 'restriction', sortable: false },
  { title: 'Data', key: 'restricted_at', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

const logHeaders = [
  { title: 'Ação', key: 'action', sortable: false },
  { title: 'Moderador', key: 'moderator', sortable: false },
  { title: 'Alvo', key: 'target', sortable: false },
  { title: 'Data', key: 'created_at', sortable: false }
]

const moderatorHeaders = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Permissões', key: 'permissions', sortable: false },
  { title: 'Adicionado em', key: 'added_at', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Helper functions
function getReasonColor(reason: string) {
  switch (reason) {
    case 'spam': return 'orange'
    case 'inappropriate': return 'red'
    case 'offensive': return 'deep-orange'
    case 'fake': return 'purple'
    default: return 'grey'
  }
}

function getReasonText(reason: string) {
  switch (reason) {
    case 'spam': return 'Spam'
    case 'inappropriate': return 'Inadequado'
    case 'offensive': return 'Ofensivo'
    case 'fake': return 'Fake News'
    default: return 'Outro'
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'pending': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'error'
    default: return 'grey'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'pending': return 'Pendente'
    case 'approved': return 'Aprovada'
    case 'rejected': return 'Rejeitada'
    default: return 'Desconhecido'
  }
}

function getRestrictionColor(restriction: string) {
  switch (restriction) {
    case 'banned': return 'error'
    case 'suspended': return 'warning'
    case 'muted': return 'info'
    default: return 'grey'
  }
}

function getRestrictionText(restriction: string) {
  switch (restriction) {
    case 'banned': return 'Banido'
    case 'suspended': return 'Suspenso'
    case 'muted': return 'Silenciado'
    default: return 'Desconhecido'
  }
}

function getActionColor(action: string) {
  switch (action) {
    case 'ban_user': return 'error'
    case 'delete_post': return 'warning'
    case 'approve_report': return 'success'
    case 'reject_report': return 'info'
    default: return 'grey'
  }
}

function getActionIcon(action: string) {
  switch (action) {
    case 'ban_user': return 'mdi-account-remove'
    case 'delete_post': return 'mdi-delete'
    case 'approve_report': return 'mdi-check'
    case 'reject_report': return 'mdi-close'
    default: return 'mdi-help'
  }
}

function getActionText(action: string) {
  switch (action) {
    case 'ban_user': return 'Banir Usuário'
    case 'delete_post': return 'Excluir Post'
    case 'approve_report': return 'Aprovar Denúncia'
    case 'reject_report': return 'Rejeitar Denúncia'
    default: return 'Ação Desconhecida'
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Actions
function viewPost(report: any) {
  console.log('Ver post:', report)
}

function approveReport(report: any) {
  console.log('Aprovar denúncia:', report)
}

function rejectReport(report: any) {
  console.log('Rejeitar denúncia:', report)
}

function deletePost(report: any) {
  console.log('Excluir post:', report)
}

function banUser(report: any) {
  console.log('Banir usuário:', report)
}

function viewUserHistory(user: any) {
  console.log('Ver histórico:', user)
}

function removeRestriction(user: any) {
  console.log('Remover restrição:', user)
}

function editModerator(moderator: any) {
  console.log('Editar moderador:', moderator)
}

function removeModerator(moderator: any) {
  console.log('Remover moderador:', moderator)
}

function loadReports() {
  console.log('Carregar denúncias com filtro:', reportFilter.value)
}

function saveSettings() {
  console.log('Salvar configurações:', settings.value)
  settingsDialog.value = false
}

onMounted(() => {
  // Load initial data
})
</script>

<style scoped>
.forum-moderation {
  padding: 24px;
}
</style>
