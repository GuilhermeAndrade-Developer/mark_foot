<template>
  <v-app>
    <!-- Show main layout only if authenticated -->
    <template v-if="authStore.isAuthenticated">
      <!-- Navigation Drawer -->
      <v-navigation-drawer
        v-model="drawer"
        app
        temporary
        :width="280"
      >
        <v-list>
          <v-list-item
            prepend-avatar="/logo.png"
            :title="authStore.fullName || 'Mark Foot'"
            :subtitle="authStore.user?.email || 'Análise de Futebol'"
          />
        </v-list>

        <v-divider />

        <!-- User Progress Widget -->
        <div class="pa-4">
          <UserProgressWidget />
        </div>

        <v-divider />

        <v-list v-model:opened="openGroups" density="compact" nav>
          <!-- Core Management Group -->
          <v-list-group value="core">
            <template #activator="{ props }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon>mdi-view-dashboard-variant</v-icon>
                </template>
                <v-list-item-title>Gestão Principal</v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="item in coreItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :to="item.route"
              color="primary"
              class="ml-2"
            />
          </v-list-group>

          <!-- Gamification Group -->
          <v-list-group value="gamification">
            <template #activator="{ props }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon>mdi-gamepad-variant</v-icon>
                </template>
                <v-list-item-title>Gamificação</v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="item in gamificationItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :to="item.route"
              color="primary"
              class="ml-2"
            />
          </v-list-group>

          <!-- Chat Features Group -->
          <v-list-group value="chat">
            <template #activator="{ props }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon>mdi-forum</v-icon>
                </template>
                <v-list-item-title>Live Chat</v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="item in chatItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :to="item.route"
              color="primary"
              class="ml-2"
            />
          </v-list-group>
          <v-list-group value="social">
            <template #activator="{ props }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon>mdi-account-group</v-icon>
                </template>
                <v-list-item-title>Recursos Sociais</v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="item in socialItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :to="item.route"
              color="primary"
              class="ml-2"
            />
          </v-list-group>

          <!-- AI Management Group -->
          <v-list-group value="ai">
            <template #activator="{ props }">
              <v-list-item v-bind="props">
                <template #prepend>
                  <v-icon>mdi-brain</v-icon>
                </template>
                <v-list-item-title>Inteligência Artificial</v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="item in aiItems"
              :key="item.title"
              :prepend-icon="item.icon"
              :title="item.title"
              :to="item.route"
              color="primary"
              class="ml-2"
            />
          </v-list-group>

          <v-divider class="my-2" />

          <!-- System Items (without group) -->
          <v-list-item
            v-for="item in systemItems"
            :key="item.title"
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.route"
            color="primary"
          />
        </v-list>

        <template #append>
          <v-divider />
          <v-list density="compact">
            <v-list-item
              prepend-icon="mdi-logout"
              title="Sair"
              @click="handleLogout"
            />
          </v-list>
        </template>
      </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar
      app
      color="primary"
      dark
      elevation="2"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <v-toolbar-title class="font-weight-bold">
        <v-icon class="mr-2">mdi-soccer</v-icon>
        Mark Foot Dashboard
      </v-toolbar-title>

      <v-spacer />

      <!-- User Menu -->
      <v-menu>
        <template #activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="mr-2"
          >
            <v-avatar size="32">
              <v-icon>mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ authStore.fullName }}</v-list-item-title>
            <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-divider />
          
          <v-list-item
            prepend-icon="mdi-logout"
            title="Sair"
            @click="handleLogout"
          />
        </v-list>
      </v-menu>

      <!-- Theme Toggle -->
      <v-btn
        icon
        @click="toggleTheme"
      >
        <v-icon>
          {{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}
        </v-icon>
      </v-btn>

      <!-- Notifications -->
      <v-btn icon>
        <v-badge
          color="error"
          content="3"
          offset-x="10"
          offset-y="10"
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>

      <!-- User Menu -->
      <v-menu>
        <template #activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar size="32">
              <v-icon>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>Admin User</v-list-item-title>
            <v-list-item-subtitle>admin@markfoot.com</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Configurações</v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>Sair</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
    </template>

    <!-- Login page for non-authenticated users -->
    <template v-else>
      <router-view />
    </template>

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

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
    >
      {{ snackbar.text }}
      <template #actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useGamificationStore } from '@/stores/gamification'
import UserProgressWidget from '@/components/UserProgressWidget.vue'

const router = useRouter()
const route = useRoute()
const theme = useTheme()
const appStore = useAppStore()
const authStore = useAuthStore()
const gamificationStore = useGamificationStore()

// Reactive data
const drawer = ref(false)
const loading = ref(false)
const openGroups = ref(['core']) // Abrir "Gestão Principal" por padrão

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Menu items with sections
const menuItems = [
  // Core Management
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    route: '/',
    section: 'core'
  },
  {
    title: 'Times',
    icon: 'mdi-shield-account',
    route: '/teams',
    section: 'core'
  },
  {
    title: 'Jogadores',
    icon: 'mdi-account-group',
    route: '/players',
    section: 'core'
  },
  {
    title: 'Partidas',
    icon: 'mdi-soccer',
    route: '/matches',
    section: 'core'
  },
  {
    title: 'Competições',
    icon: 'mdi-trophy',
    route: '/competitions',
    section: 'core'
  },
  {
    title: 'Classificação',
    icon: 'mdi-podium',
    route: '/standings',
    section: 'core'
  },
  {
    title: 'Estatísticas',
    icon: 'mdi-chart-line',
    route: '/statistics',
    section: 'core'
  },
  // Gamification Management
  {
    title: 'Gamificação',
    icon: 'mdi-gamepad-variant',
    route: '/gamification',
    section: 'gamification'
  },
  {
    title: 'Gestão de Usuários',
    icon: 'mdi-account-cog',
    route: '/gamification/users',
    section: 'gamification'
  },
  {
    title: 'Analytics',
    icon: 'mdi-chart-line-variant',
    route: '/gamification/analytics',
    section: 'gamification'
  },
  // Social Management
  {
    title: 'Social Dashboard',
    icon: 'mdi-account-multiple',
    route: '/social',
    section: 'social'
  },
  {
    title: 'Fórum',
    icon: 'mdi-forum-outline',
    route: '/forum',
    section: 'social'
  },
  {
    title: 'Categorias',
    icon: 'mdi-folder-outline',
    route: '/forum/categories',
    section: 'social'
  },
  {
    title: 'Gerenciar Tópicos',
    icon: 'mdi-forum',
    route: '/forum/topics',
    section: 'social'
  },
  {
    title: 'Moderação',
    icon: 'mdi-shield-check',
    route: '/forum/moderation',
    section: 'social'
  },
  {
    title: 'Relatórios',
    icon: 'mdi-chart-box',
    route: '/forum/reports',
    section: 'social'
  },
  {
    title: 'Gestão de Comentários',
    icon: 'mdi-comment-multiple',
    route: '/social/comments',
    section: 'social'
  },
  {
    title: 'Usuários Sociais',
    icon: 'mdi-account-heart',
    route: '/social/users',
    section: 'social'
  },
  // Chat Management
  {
    title: 'Chat Dashboard',
    icon: 'mdi-forum',
    route: '/chat',
    section: 'chat'
  },
  {
    title: 'Gerenciar Salas',
    icon: 'mdi-door-open',
    route: '/chat/rooms',
    section: 'chat'
  },
  {
    title: 'Moderação de Chat',
    icon: 'mdi-shield-check',
    route: '/chat/moderation',
    section: 'chat'
  },
  // AI Management
  {
    title: 'IA Dashboard',
    icon: 'mdi-brain',
    route: '/ai-dashboard',
    section: 'ai'
  },
  {
    title: 'Análise de Sentimento',
    icon: 'mdi-heart-pulse',
    route: '/ai-sentiment',
    section: 'ai'
  },
  {
    title: 'Testes IA',
    icon: 'mdi-test-tube',
    route: '/ai-testing',
    section: 'ai'
  },
  // System
  {
    title: 'Configurações',
    icon: 'mdi-cog',
    route: '/settings',
    section: 'system'
  }
]

// Computed properties for menu sections
const coreItems = computed(() => menuItems.filter(item => item.section === 'core'))
const gamificationItems = computed(() => menuItems.filter(item => item.section === 'gamification'))
const socialItems = computed(() => menuItems.filter(item => item.section === 'social'))
const chatItems = computed(() => menuItems.filter(item => item.section === 'chat'))
const aiItems = computed(() => menuItems.filter(item => item.section === 'ai'))
const systemItems = computed(() => menuItems.filter(item => item.section === 'system'))

// Function to get current section based on route
const getCurrentSection = () => {
  const currentPath = route.path
  const currentItem = menuItems.find(item => item.route === currentPath)
  return currentItem?.section || 'core'
}

// Watch route changes to expand the correct group
watch(() => route.path, () => {
  const currentSection = getCurrentSection()
  if (!openGroups.value.includes(currentSection)) {
    openGroups.value = [currentSection]
  }
}, { immediate: true })

// Methods
const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}

// Methods
const handleLogout = async () => {
  try {
    loading.value = true
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Erro no logout:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Initialize authentication
  authStore.initializeAuth()
  
  // Initialize gamification if authenticated (will use fallback if API not available)
  if (authStore.isAuthenticated) {
    gamificationStore.initializeGamification().catch(() => {
      console.log('Gamificação inicializada com dados de demonstração')
    })
  }
})
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-toolbar-title {
  font-size: 1.25rem !important;
}

/* Menu group styling */
.v-list-group__items .v-list-item {
  border-left: 2px solid rgba(var(--v-theme-primary), 0.1);
  margin-left: 4px;
  margin-bottom: 2px;
}

.v-list-group__items .v-list-item:hover {
  border-left-color: rgba(var(--v-theme-primary), 0.3);
}

.v-list-group__items .v-list-item--active {
  border-left-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.08);
}

/* Group activator styling */
.v-list-group > .v-list-item {
  font-weight: 500;
}

.v-list-group > .v-list-item .v-list-item__prepend > .v-icon {
  opacity: 0.8;
}
</style>
