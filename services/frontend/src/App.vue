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

        <v-list density="compact" nav>
          <v-list-item
            v-for="item in menuItems"
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const theme = useTheme()
const appStore = useAppStore()
const authStore = useAuthStore()

// Reactive data
const drawer = ref(false)
const loading = ref(false)

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Menu items
const menuItems = [
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    route: '/'
  },
  {
    title: 'Times',
    icon: 'mdi-shield-account',
    route: '/teams'
  },
  {
    title: 'Jogadores',
    icon: 'mdi-account-group',
    route: '/players'
  },
  {
    title: 'Partidas',
    icon: 'mdi-soccer',
    route: '/matches'
  },
  {
    title: 'Competições',
    icon: 'mdi-trophy',
    route: '/competitions'
  },
  {
    title: 'Classificação',
    icon: 'mdi-podium',
    route: '/standings'
  },
  {
    title: 'Estatísticas',
    icon: 'mdi-chart-line',
    route: '/statistics'
  },
  // AI Management Section
  {
    title: 'IA Dashboard',
    icon: 'mdi-brain',
    route: '/ai-dashboard'
  },
  {
    title: 'Análise de Sentimento',
    icon: 'mdi-heart',
    route: '/ai-sentiment'
  },
  {
    title: 'Testes IA',
    icon: 'mdi-test-tube',
    route: '/ai-testing'
  }
]

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
})
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-toolbar-title {
  font-size: 1.25rem !important;
}
</style>
