<template>
  <v-app>
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
          title="Mark Foot"
          subtitle="Análise de Futebol"
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
import { ref, reactive } from 'vue'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/stores/app'

const theme = useTheme()
const appStore = useAppStore()

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
  }
]

// Methods
const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-toolbar-title {
  font-size: 1.25rem !important;
}
</style>
