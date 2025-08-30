<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-cog</v-icon>
          Configurações de Redes Sociais
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Configure integrações com APIs das redes sociais
        </p>
      </v-col>
    </v-row>

    <!-- Demo Mode Alert -->
    <v-alert
      v-if="isDemoMode"
      type="info"
      variant="tonal"
      class="mb-6"
      prominent
    >
      <template #prepend>
        <v-icon>mdi-information</v-icon>
      </template>
      <v-alert-title>Modo Demonstração</v-alert-title>
      <p>
        Você está visualizando dados de demonstração. Para usar dados reais, 
        configure as integrações com as APIs das redes sociais abaixo.
      </p>
    </v-alert>

    <!-- Platform Configuration Cards -->
    <v-row>
      <v-col
        v-for="platform in platforms"
        :key="platform.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card elevation="3" class="platform-card">
          <v-card-title class="d-flex align-center">
            <v-avatar
              :color="getPlatformColor(platform.name)"
              size="40"
              class="mr-3"
            >
              <v-icon color="white">
                {{ getPlatformIcon(platform.name) }}
              </v-icon>
            </v-avatar>
            <div>
              <div class="text-h6">{{ platform.display_name }}</div>
              <v-chip
                :color="platform.is_active ? 'success' : 'error'"
                size="small"
                class="mt-1"
              >
                {{ platform.is_active ? 'Configurado' : 'Não Configurado' }}
              </v-chip>
            </div>
          </v-card-title>

          <v-card-text>
            <div class="mb-4">
              <div class="text-subtitle-2 mb-2">Limitações da Plataforma:</div>
              <v-chip size="small" class="mr-2 mb-1">
                <v-icon start size="16">mdi-text</v-icon>
                {{ platform.character_limit }} caracteres
              </v-chip>
              <v-chip v-if="platform.supports_images" size="small" class="mr-2 mb-1" color="success">
                <v-icon start size="16">mdi-image</v-icon>
                Imagens
              </v-chip>
              <v-chip v-if="platform.supports_videos" size="small" class="mr-2 mb-1" color="info">
                <v-icon start size="16">mdi-video</v-icon>
                Vídeos
              </v-chip>
              <v-chip v-if="platform.supports_hashtags" size="small" class="mr-2 mb-1" color="secondary">
                <v-icon start size="16">mdi-pound</v-icon>
                Hashtags
              </v-chip>
            </div>

            <div v-if="platform.is_active" class="mb-4">
              <div class="text-subtitle-2 mb-2 text-success">Status da Configuração:</div>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon color="success" size="20">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">API Key configurada</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template #prepend>
                    <v-icon color="success" size="20">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">Webhooks configurados</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template #prepend>
                    <v-icon color="success" size="20">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">Permissões validadas</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>

            <div v-else class="mb-4">
              <div class="text-subtitle-2 mb-2 text-warning">Pendências de Configuração:</div>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon color="warning" size="20">mdi-alert-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">API Key não configurada</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template #prepend>
                    <v-icon color="warning" size="20">mdi-alert-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">Webhooks pendentes</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template #prepend>
                    <v-icon color="error" size="20">mdi-close-circle</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">Permissões não validadas</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>

          <v-card-actions>
            <v-btn
              :color="platform.is_active ? 'primary' : 'success'"
              variant="outlined"
              block
              @click="openConfigDialog(platform)"
            >
              <v-icon start>{{ platform.is_active ? 'mdi-cog' : 'mdi-plus' }}</v-icon>
              {{ platform.is_active ? 'Reconfigurar' : 'Configurar Agora' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- General Settings -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-tune</v-icon>
            Configurações Gerais
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="generalSettings.auto_share_matches"
                  label="Compartilhamento automático de resultados"
                  color="primary"
                  hide-details
                />
                <p class="text-caption text-medium-emphasis mt-1">
                  Compartilha automaticamente resultados de partidas
                </p>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-switch
                  v-model="generalSettings.auto_invite_groups"
                  label="Convites automáticos para grupos"
                  color="primary"
                  hide-details
                />
                <p class="text-caption text-medium-emphasis mt-1">
                  Sugere automaticamente grupos para novos usuários
                </p>
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="generalSettings.default_share_platform"
                  :items="activePlatforms"
                  item-title="display_name"
                  item-value="id"
                  label="Plataforma padrão para compartilhamento"
                  outlined
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="generalSettings.webhook_url"
                  label="URL de Webhook para notificações"
                  placeholder="https://seu-site.com/webhook"
                  outlined
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="generalSettings.default_hashtags"
                  label="Hashtags padrão"
                  placeholder="#markfoot #futebol #analise"
                  rows="3"
                  outlined
                />
              </v-col>
            </v-row>

            <v-divider class="my-6" />

            <div class="d-flex justify-end">
              <v-btn
                color="primary"
                :loading="saving"
                @click="saveGeneralSettings"
              >
                <v-icon start>mdi-content-save</v-icon>
                Salvar Configurações
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Configuration Dialog -->
    <v-dialog v-model="showConfigDialog" max-width="800">
      <v-card v-if="selectedPlatform">
        <v-card-title>
          <v-avatar
            :color="getPlatformColor(selectedPlatform.name)"
            size="32"
            class="mr-3"
          >
            <v-icon color="white" size="16">
              {{ getPlatformIcon(selectedPlatform.name) }}
            </v-icon>
          </v-avatar>
          Configurar {{ selectedPlatform.display_name }}
        </v-card-title>

        <v-card-text>
          <v-stepper v-model="configStep" alt-labels>
            <v-stepper-header>
              <v-stepper-item :complete="configStep > 1" :value="1" title="API Keys" />
              <v-divider />
              <v-stepper-item :complete="configStep > 2" :value="2" title="Webhooks" />
              <v-divider />
              <v-stepper-item :complete="configStep > 3" :value="3" title="Teste" />
            </v-stepper-header>

            <v-stepper-window>
              <!-- Step 1: API Keys -->
              <v-stepper-window-item :value="1">
                <v-form v-model="configForm.valid">
                  <v-alert type="info" variant="tonal" class="mb-4">
                    <v-alert-title>Instruções para {{ selectedPlatform.display_name }}</v-alert-title>
                    <p>{{ getConfigInstructions(selectedPlatform.name) }}</p>
                  </v-alert>

                  <v-text-field
                    v-model="configForm.api_key"
                    label="API Key"
                    :type="showApiKey ? 'text' : 'password'"
                    :rules="[v => !!v || 'API Key é obrigatória']"
                    required
                  >
                    <template #append-inner>
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        @click="showApiKey = !showApiKey"
                      >
                        <v-icon>{{ showApiKey ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </v-btn>
                    </template>
                  </v-text-field>

                  <v-text-field
                    v-model="configForm.api_secret"
                    label="API Secret"
                    :type="showApiSecret ? 'text' : 'password'"
                    :rules="[v => !!v || 'API Secret é obrigatório']"
                    required
                  >
                    <template #append-inner>
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        @click="showApiSecret = !showApiSecret"
                      >
                        <v-icon>{{ showApiSecret ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </v-btn>
                    </template>
                  </v-text-field>

                  <v-text-field
                    v-if="selectedPlatform.name !== 'tiktok'"
                    v-model="configForm.access_token"
                    label="Access Token"
                    :type="showAccessToken ? 'text' : 'password'"
                  >
                    <template #append-inner>
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        @click="showAccessToken = !showAccessToken"
                      >
                        <v-icon>{{ showAccessToken ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </v-btn>
                    </template>
                  </v-text-field>
                </v-form>
              </v-stepper-window-item>

              <!-- Step 2: Webhooks -->
              <v-stepper-window-item :value="2">
                <v-alert type="warning" variant="tonal" class="mb-4">
                  <v-alert-title>Configuração de Webhooks</v-alert-title>
                  <p>Configure estes URLs nos webhooks da {{ selectedPlatform.display_name }}:</p>
                </v-alert>

                <v-list>
                  <v-list-item>
                    <v-list-item-title>URL de Callback:</v-list-item-title>
                    <v-list-item-subtitle class="font-mono">
                      {{ getWebhookUrl('callback', selectedPlatform.name) }}
                    </v-list-item-subtitle>
                    <template #append>
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        @click="copyToClipboard(getWebhookUrl('callback', selectedPlatform.name))"
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                    </template>
                  </v-list-item>

                  <v-list-item>
                    <v-list-item-title>URL de Notificação:</v-list-item-title>
                    <v-list-item-subtitle class="font-mono">
                      {{ getWebhookUrl('notification', selectedPlatform.name) }}
                    </v-list-item-subtitle>
                    <template #append>
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        @click="copyToClipboard(getWebhookUrl('notification', selectedPlatform.name))"
                      >
                        <v-icon>mdi-content-copy</v-icon>
                      </v-btn>
                    </template>
                  </v-list-item>
                </v-list>

                <v-checkbox
                  v-model="configForm.webhooks_configured"
                  label="Confirmo que configurei os webhooks na plataforma"
                  color="primary"
                />
              </v-stepper-window-item>

              <!-- Step 3: Test -->
              <v-stepper-window-item :value="3">
                <div class="text-center">
                  <v-icon size="64" :color="testResult ? 'success' : 'warning'">
                    {{ testResult ? 'mdi-check-circle' : 'mdi-help-circle' }}
                  </v-icon>
                  <h3 class="text-h6 mt-4 mb-2">
                    {{ testResult ? 'Configuração Válida!' : 'Testar Configuração' }}
                  </h3>
                  <p class="text-body-2 text-medium-emphasis mb-4">
                    {{ testResult ? 
                      'A integração foi configurada com sucesso e está funcionando.' :
                      'Clique no botão abaixo para testar a configuração.'
                    }}
                  </p>
                  
                  <v-btn
                    v-if="!testResult"
                    color="primary"
                    size="large"
                    :loading="testing"
                    @click="testConfiguration"
                  >
                    <v-icon start>mdi-test-tube</v-icon>
                    Testar Configuração
                  </v-btn>

                  <div v-if="testResult" class="mt-4">
                    <v-chip color="success" size="large">
                      <v-icon start>mdi-check</v-icon>
                      Teste realizado com sucesso
                    </v-chip>
                  </div>
                </div>
              </v-stepper-window-item>
            </v-stepper-window>
          </v-stepper>
        </v-card-text>

        <v-card-actions>
          <v-btn variant="text" @click="showConfigDialog = false">
            Cancelar
          </v-btn>
          <v-spacer />
          <v-btn
            v-if="configStep > 1"
            variant="text"
            @click="configStep--"
          >
            Anterior
          </v-btn>
          <v-btn
            v-if="configStep < 3"
            color="primary"
            :disabled="!canProceed"
            @click="configStep++"
          >
            Próximo
          </v-btn>
          <v-btn
            v-if="configStep === 3 && testResult"
            color="success"
            :loading="saving"
            @click="saveConfiguration"
          >
            Salvar Configuração
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      />
    </v-overlay>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
    >
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { SocialSharingApiService } from '@/services/socialSharingApi'
import type { SocialPlatform } from '@/services/socialSharingApi'

// Reactive data
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const showConfigDialog = ref(false)
const configStep = ref(1)
const testResult = ref(false)
const showApiKey = ref(false)
const showApiSecret = ref(false)
const showAccessToken = ref(false)

const platforms = ref<SocialPlatform[]>([])
const selectedPlatform = ref<SocialPlatform | null>(null)
const isDemoMode = ref(true)

const configForm = reactive({
  valid: false,
  api_key: '',
  api_secret: '',
  access_token: '',
  webhooks_configured: false
})

const generalSettings = reactive({
  auto_share_matches: true,
  auto_invite_groups: false,
  default_share_platform: null as number | null,
  webhook_url: '',
  default_hashtags: '#markfoot #futebol #analise'
})

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Computed
const activePlatforms = computed(() => platforms.value.filter(p => p.is_active))

const canProceed = computed(() => {
  if (configStep.value === 1) {
    return configForm.valid
  }
  if (configStep.value === 2) {
    return configForm.webhooks_configured
  }
  return true
})

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    try {
      const platformsData = await SocialSharingApiService.getPlatforms()
      
      if (platformsData.length > 0) {
        isDemoMode.value = false
        platforms.value = platformsData
      } else {
        loadDemoData()
      }
    } catch (error) {
      console.log('API não disponível, carregando dados de demonstração')
      loadDemoData()
    }
  } finally {
    loading.value = false
  }
}

const loadDemoData = () => {
  isDemoMode.value = true
  
  platforms.value = [
    {
      id: 1,
      name: 'twitter',
      display_name: 'Twitter',
      is_active: true,
      character_limit: 280,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 2,
      name: 'instagram',
      display_name: 'Instagram',
      is_active: true,
      character_limit: 2200,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 3,
      name: 'tiktok',
      display_name: 'TikTok',
      is_active: false,
      character_limit: 2200,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 4,
      name: 'facebook',
      display_name: 'Facebook',
      is_active: true,
      character_limit: 63206,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]
}

const openConfigDialog = (platform: SocialPlatform) => {
  selectedPlatform.value = platform
  configStep.value = 1
  testResult.value = false
  
  // Reset form
  configForm.api_key = ''
  configForm.api_secret = ''
  configForm.access_token = ''
  configForm.webhooks_configured = false
  
  showConfigDialog.value = true
}

const getConfigInstructions = (platformName: string) => {
  const instructions = {
    twitter: 'Acesse o Twitter Developer Portal, crie uma aplicação e obtenha as chaves API.',
    instagram: 'Configure uma aplicação no Facebook for Developers para acessar a Instagram API.',
    tiktok: 'Registre-se no TikTok for Developers e configure sua aplicação.',
    facebook: 'Acesse o Facebook for Developers e crie uma nova aplicação.'
  }
  return instructions[platformName as keyof typeof instructions] || 'Configure as credenciais da API.'
}

const getWebhookUrl = (type: string, platformName: string) => {
  const baseUrl = window.location.origin
  return `${baseUrl}/api/webhooks/${platformName}/${type}/`
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    showSnackbar('URL copiada para a área de transferência!', 'success')
  } catch {
    showSnackbar('Erro ao copiar URL', 'error')
  }
}

const testConfiguration = async () => {
  try {
    testing.value = true
    
    // Simulate API test - in real app this would call the actual API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    testResult.value = true
    showSnackbar('Configuração testada com sucesso!', 'success')
  } catch (error) {
    showSnackbar('Erro ao testar configuração', 'error')
  } finally {
    testing.value = false
  }
}

const saveConfiguration = async () => {
  try {
    saving.value = true
    
    if (!selectedPlatform.value) return
    
    if (!isDemoMode.value) {
      // In real app, save to API
      await SocialSharingApiService.updatePlatform(selectedPlatform.value.id, {
        is_active: true
      })
    } else {
      // Update demo data
      const platform = platforms.value.find(p => p.id === selectedPlatform.value?.id)
      if (platform) {
        platform.is_active = true
      }
    }
    
    showSnackbar('Configuração salva com sucesso!', 'success')
    showConfigDialog.value = false
  } catch (error) {
    showSnackbar('Erro ao salvar configuração', 'error')
  } finally {
    saving.value = false
  }
}

const saveGeneralSettings = async () => {
  try {
    saving.value = true
    
    // In real app, save to API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    showSnackbar('Configurações salvas com sucesso!', 'success')
  } catch (error) {
    showSnackbar('Erro ao salvar configurações', 'error')
  } finally {
    saving.value = false
  }
}

const showSnackbar = (text: string, color: string) => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

const getPlatformIcon = (platformName: string) => {
  const icons = {
    twitter: 'mdi-twitter',
    instagram: 'mdi-instagram',
    tiktok: 'mdi-music-note',
    facebook: 'mdi-facebook'
  }
  return icons[platformName as keyof typeof icons] || 'mdi-web'
}

const getPlatformColor = (platformName: string) => {
  const colors = {
    twitter: '#1DA1F2',
    instagram: '#E4405F',
    tiktok: '#000000',
    facebook: '#4267B2'
  }
  return colors[platformName as keyof typeof colors] || 'primary'
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.platform-card {
  transition: all 0.3s ease;
}

.platform-card:hover {
  transform: translateY(-2px);
}

.font-mono {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.v-stepper {
  box-shadow: none;
}
</style>
