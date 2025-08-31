<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-shield-check</v-icon>
          Moderação de Chat
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Monitore e modere atividades dos chats em tempo real
        </p>
      </v-col>
    </v-row>

    <!-- Alert Summary -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-card color="error" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-alert</v-icon>
            <div class="text-h5 font-weight-bold">2</div>
            <div class="text-subtitle-2">Alertas Críticos</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-flag</v-icon>
            <div class="text-h5 font-weight-bold">8</div>
            <div class="text-subtitle-2">Mensagens Flagadas</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="info" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-account-alert</v-icon>
            <div class="text-h5 font-weight-bold">3</div>
            <div class="text-subtitle-2">Denúncias Pendentes</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="grey" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-account-cancel</v-icon>
            <div class="text-h5 font-weight-bold">5</div>
            <div class="text-subtitle-2">Usuários Banidos</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="flagged">Mensagens Flagadas</v-tab>
      <v-tab value="reports">Denúncias</v-tab>
      <v-tab value="banned">Usuários Banidos</v-tab>
      <v-tab value="moderation">Ações de Moderação</v-tab>
    </v-tabs>

    <!-- Flagged Messages Tab -->
    <v-window v-model="activeTab">
      <v-window-item value="flagged">
        <v-card elevation="2">
          <v-card-title>Mensagens Flagadas</v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                v-for="message in flaggedMessages"
                :key="message.id"
                cols="12"
              >
                <v-card variant="outlined" class="mb-3">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="8">
                        <div class="d-flex align-center mb-2">
                          <v-avatar size="32" class="mr-3">
                            <v-icon>mdi-account</v-icon>
                          </v-avatar>
                          <div>
                            <div class="font-weight-medium">{{ message.user_name }}</div>
                            <div class="text-caption text-medium-emphasis">
                              {{ message.room_name }} - {{ message.created_at }}
                            </div>
                          </div>
                        </div>
                        
                        <div class="message-content">
                          <div class="original-message mb-2">{{ message.content }}</div>
                          <div class="d-flex flex-wrap ga-1">
                            <v-chip
                              v-for="flag in message.flags"
                              :key="flag"
                              size="x-small"
                              :color="getFlagColor(flag)"
                              variant="flat"
                            >
                              {{ getFlagLabel(flag) }}
                            </v-chip>
                          </div>
                        </div>
                      </v-col>
                      
                      <v-col cols="12" md="4">
                        <div class="d-flex flex-column ga-2">
                          <v-chip
                            :color="getSeverityColor(message.severity)"
                            size="small"
                            variant="tonal"
                          >
                            {{ getSeverityLabel(message.severity) }}
                          </v-chip>
                          
                          <div class="d-flex ga-1">
                            <v-btn
                              size="small"
                              color="success"
                              variant="outlined"
                              @click="approveMessage(message)"
                            >
                              Aprovar
                            </v-btn>
                            
                            <v-btn
                              size="small"
                              color="error"
                              variant="outlined"
                              @click="deleteMessage(message)"
                            >
                              Deletar
                            </v-btn>
                          </div>
                          
                          <v-btn
                            size="small"
                            color="warning"
                            variant="outlined"
                            @click="warnUser(message)"
                          >
                            Advertir Usuário
                          </v-btn>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Reports Tab -->
      <v-window-item value="reports">
        <v-card elevation="2">
          <v-card-title>Denúncias</v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                v-for="report in reports"
                :key="report.id"
                cols="12"
              >
                <v-card variant="outlined" class="mb-3">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <div class="d-flex align-center mb-2">
                          <v-avatar size="32" class="mr-3">
                            <v-icon>mdi-account</v-icon>
                          </v-avatar>
                          <div>
                            <div class="font-weight-medium">{{ report.reporter_name }}</div>
                            <div class="text-caption text-medium-emphasis">
                              Denunciou: {{ report.reported_user_name }}
                            </div>
                          </div>
                        </div>
                        
                        <div>
                          <v-chip
                            :color="getReasonColor(report.reason)"
                            size="small"
                            variant="tonal"
                            class="mb-2"
                          >
                            {{ getReasonLabel(report.reason) }}
                          </v-chip>
                          <div>{{ report.description }}</div>
                        </div>
                      </v-col>
                      
                      <v-col cols="12" md="3">
                        <div class="text-caption text-medium-emphasis">Sala:</div>
                        <div class="font-weight-medium">{{ report.room_name }}</div>
                        <div class="text-caption text-medium-emphasis mt-2">Data:</div>
                        <div>{{ report.created_at }}</div>
                      </v-col>
                      
                      <v-col cols="12" md="3">
                        <div class="d-flex flex-column ga-2">
                          <v-btn
                            size="small"
                            color="primary"
                            variant="outlined"
                            @click="reviewReport(report)"
                          >
                            Analisar
                          </v-btn>
                          
                          <v-btn
                            size="small"
                            color="success"
                            variant="outlined"
                            @click="dismissReport(report)"
                          >
                            Dispensar
                          </v-btn>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Banned Users Tab -->
      <v-window-item value="banned">
        <v-card elevation="2">
          <v-card-title>Usuários Banidos</v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                v-for="ban in bannedUsers"
                :key="ban.id"
                cols="12"
              >
                <v-card variant="outlined" class="mb-3">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="4">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3">
                            <v-icon>mdi-account-cancel</v-icon>
                          </v-avatar>
                          <div>
                            <div class="font-weight-medium">{{ ban.user_name }}</div>
                            <div class="text-caption text-medium-emphasis">
                              ID: {{ ban.user_id }}
                            </div>
                          </div>
                        </div>
                      </v-col>
                      
                      <v-col cols="12" md="4">
                        <div>
                          <div class="font-weight-medium">{{ ban.reason }}</div>
                          <div class="text-caption text-medium-emphasis">
                            Por: {{ ban.banned_by_name }}
                          </div>
                          <div class="text-caption text-medium-emphasis">
                            {{ ban.banned_at }}
                          </div>
                        </div>
                      </v-col>
                      
                      <v-col cols="12" md="2">
                        <div v-if="ban.ban_until">
                          <div class="font-weight-medium">{{ ban.ban_until }}</div>
                          <div class="text-caption text-success">
                            {{ ban.remaining_time }}
                          </div>
                        </div>
                        <div v-else class="text-error font-weight-medium">
                          Permanente
                        </div>
                      </v-col>
                      
                      <v-col cols="12" md="2">
                        <div class="d-flex ga-1">
                          <v-btn
                            size="small"
                            color="warning"
                            variant="outlined"
                            @click="unbanUser(ban)"
                          >
                            Desbanir
                          </v-btn>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Moderation Actions Tab -->
      <v-window-item value="moderation">
        <v-card elevation="2">
          <v-card-title>Ações de Moderação</v-card-title>
          <v-card-text>
            <v-timeline density="compact">
              <v-timeline-item
                v-for="action in moderationActions"
                :key="action.id"
                :dot-color="getActionColor(action.action_type)"
                size="small"
              >
                <v-card variant="outlined">
                  <v-card-text class="py-2">
                    <div class="d-flex justify-space-between align-center">
                      <div>
                        <div class="font-weight-medium">
                          <v-chip
                            :color="getActionColor(action.action_type)"
                            size="small"
                            variant="tonal"
                            class="mr-2"
                          >
                            {{ getActionLabel(action.action_type) }}
                          </v-chip>
                          {{ action.moderator_name }}
                        </div>
                        <div class="text-caption text-medium-emphasis">
                          Alvo: {{ action.target_user_name }} - {{ action.room_name }}
                        </div>
                        <div class="text-caption">{{ action.reason }}</div>
                      </div>
                      <div class="text-caption">{{ action.created_at }}</div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Info Alert -->
    <v-row class="mt-6">
      <v-col>
        <v-alert
          type="info"
          variant="tonal"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-3">mdi-information</v-icon>
            <div>
              <strong>Demo Mode:</strong> Esta é uma demonstração do sistema de moderação. 
              Os dados mostrados são exemplos para ilustrar as funcionalidades disponíveis.
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const activeTab = ref('flagged')

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})

// Demo data
const flaggedMessages = ref([
  {
    id: 1,
    content: 'Este time é uma vergonha! Técnico incompetente!',
    user_name: 'torcedor123',
    room_name: 'Real Madrid Fan Club',
    created_at: 'há 5 min',
    flags: ['profanity', 'harassment'],
    severity: 'high'
  },
  {
    id: 2,
    content: 'Spam spam spam compre aqui link.com',
    user_name: 'spammer456',
    room_name: 'Chat Geral',
    created_at: 'há 10 min',
    flags: ['spam', 'suspicious_link'],
    severity: 'medium'
  }
])

const reports = ref([
  {
    id: 1,
    reporter_name: 'usuario_limpo',
    reported_user_name: 'baduser123',
    reason: 'harassment',
    description: 'Usuário enviando mensagens ofensivas constantemente',
    room_name: 'Premier League Chat',
    created_at: 'há 15 min'
  },
  {
    id: 2,
    reporter_name: 'moderador_voluntario',
    reported_user_name: 'fake_account',
    reason: 'fake_profile',
    description: 'Perfil claramente falso com informações suspeitas',
    room_name: 'Liverpool vs Arsenal',
    created_at: 'há 1 hora'
  }
])

const bannedUsers = ref([
  {
    id: 1,
    user_name: 'toxic_user',
    user_id: '12345',
    reason: 'Assédio repetido a outros usuários',
    banned_by_name: 'Admin',
    banned_at: '2025-08-28 10:30',
    ban_until: '2025-08-30 10:30',
    remaining_time: 'em 2 dias'
  },
  {
    id: 2,
    user_name: 'spammer_pro',
    user_id: '67890',
    reason: 'Spam excessivo em múltiplas salas',
    banned_by_name: 'ModeradorChefe',
    banned_at: '2025-08-27 15:20',
    ban_until: null,
    remaining_time: null
  }
])

const moderationActions = ref([
  {
    id: 1,
    action_type: 'warn',
    moderator_name: 'Admin',
    target_user_name: 'usuario_problema',
    room_name: 'Chat Geral',
    reason: 'Linguagem inapropriada',
    created_at: 'há 30 min'
  },
  {
    id: 2,
    action_type: 'delete_message',
    moderator_name: 'Sistema',
    target_user_name: 'spammer',
    room_name: 'Real Madrid Fan Club',
    reason: 'Detecção automática de spam',
    created_at: 'há 1 hora'
  },
  {
    id: 3,
    action_type: 'ban',
    moderator_name: 'ModeradorChefe',
    target_user_name: 'toxic_user',
    room_name: 'Premier League Chat',
    reason: 'Assédio repetido',
    created_at: 'há 2 horas'
  }
])

// Utility functions
const getFlagColor = (flag: string) => {
  switch (flag) {
    case 'spam': return 'orange'
    case 'profanity': return 'red'
    case 'harassment': return 'purple'
    case 'inappropriate': return 'pink'
    case 'suspicious_link': return 'yellow'
    default: return 'grey'
  }
}

const getFlagLabel = (flag: string) => {
  switch (flag) {
    case 'spam': return 'Spam'
    case 'profanity': return 'Palavrão'
    case 'harassment': return 'Assédio'
    case 'inappropriate': return 'Inapropriado'
    case 'suspicious_link': return 'Link Suspeito'
    default: return flag
  }
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'low': return 'green'
    case 'medium': return 'orange'
    case 'high': return 'red'
    case 'critical': return 'purple'
    default: return 'grey'
  }
}

const getSeverityLabel = (severity: string) => {
  switch (severity) {
    case 'low': return 'Baixa'
    case 'medium': return 'Média'
    case 'high': return 'Alta'
    case 'critical': return 'Crítica'
    default: return severity
  }
}

const getReasonColor = (reason: string) => {
  switch (reason) {
    case 'spam': return 'orange'
    case 'harassment': return 'red'
    case 'inappropriate': return 'purple'
    case 'fake_profile': return 'pink'
    default: return 'grey'
  }
}

const getReasonLabel = (reason: string) => {
  switch (reason) {
    case 'spam': return 'Spam'
    case 'harassment': return 'Assédio'
    case 'inappropriate': return 'Inapropriado'
    case 'fake_profile': return 'Perfil Falso'
    default: return reason
  }
}

const getActionColor = (action: string) => {
  switch (action) {
    case 'warn': return 'yellow'
    case 'mute': return 'orange'
    case 'ban': return 'red'
    case 'unban': return 'green'
    case 'delete_message': return 'purple'
    default: return 'grey'
  }
}

const getActionLabel = (action: string) => {
  switch (action) {
    case 'warn': return 'Advertência'
    case 'mute': return 'Silenciado'
    case 'ban': return 'Banido'
    case 'unban': return 'Desbanido'
    case 'delete_message': return 'Mensagem Deletada'
    default: return action
  }
}

const showMessage = (text: string, color = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

// Action methods
const approveMessage = (message: any) => {
  const index = flaggedMessages.value.findIndex(m => m.id === message.id)
  if (index > -1) {
    flaggedMessages.value.splice(index, 1)
    showMessage('Mensagem aprovada')
  }
}

const deleteMessage = (message: any) => {
  const index = flaggedMessages.value.findIndex(m => m.id === message.id)
  if (index > -1) {
    flaggedMessages.value.splice(index, 1)
    showMessage('Mensagem deletada', 'warning')
  }
}

const warnUser = (message: any) => {
  showMessage(`Usuário ${message.user_name} advertido`, 'warning')
}

const reviewReport = (report: any) => {
  showMessage(`Analisando denúncia de ${report.reporter_name}`, 'info')
}

const dismissReport = (report: any) => {
  const index = reports.value.findIndex(r => r.id === report.id)
  if (index > -1) {
    reports.value.splice(index, 1)
    showMessage('Denúncia dispensada')
  }
}

const unbanUser = (ban: any) => {
  const index = bannedUsers.value.findIndex(b => b.id === ban.id)
  if (index > -1) {
    bannedUsers.value.splice(index, 1)
    showMessage(`Usuário ${ban.user_name} desbanido`)
  }
}
</script>

<style scoped>
.message-content {
  max-width: 100%;
}

.original-message {
  font-weight: medium;
  padding: 8px 12px;
  background: rgba(var(--v-theme-surface), 0.5);
  border-radius: 4px;
}

.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-1px);
}
</style>
