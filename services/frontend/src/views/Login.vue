<template>
  <v-row justify="center" align="center" class="login-container">
    <v-col cols="12" sm="8" md="6" lg="4">
      <v-card elevation="8" class="pa-6">
        <v-card-title class="text-center mb-4">
          <div class="d-flex flex-column align-center">
            <v-icon 
              size="64" 
              color="primary" 
              class="mb-3"
            >
              mdi-soccer
            </v-icon>
            <h2 class="text-h4 font-weight-bold text-primary">
              Mark Foot
            </h2>
            <p class="text-subtitle-1 text-medium-emphasis">
              Sistema de Análise de Futebol
            </p>
          </div>
        </v-card-title>

        <v-card-text>
          <v-form @submit.prevent="handleLogin">
            <v-text-field
              v-model="loginForm.username"
              label="Usuário"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              :error-messages="errors.username"
              @input="clearError('username')"
              autofocus
            />

            <v-text-field
              v-model="loginForm.password"
              label="Senha"
              prepend-inner-icon="mdi-lock"
              :type="showPassword ? 'text' : 'password'"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              variant="outlined"
              :error-messages="errors.password"
              @click:append-inner="showPassword = !showPassword"
              @input="clearError('password')"
              @keyup.enter="handleLogin"
            />

            <v-checkbox
              v-model="rememberMe"
              label="Lembrar de mim"
              density="compact"
              class="mb-2"
            />

            <v-alert
              v-if="generalError"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="generalError = ''"
            >
              {{ generalError }}
            </v-alert>

            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="loading"
              :disabled="!isFormValid"
              class="mb-4"
            >
              <v-icon start>mdi-login</v-icon>
              Entrar
            </v-btn>

            <div class="text-center">
              <v-btn
                variant="text"
                size="small"
                @click="showForgotPassword = true"
              >
                Esqueceu a senha?
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>

    <!-- Forgot Password Dialog -->
    <v-dialog
      v-model="showForgotPassword"
      max-width="400"
    >
      <v-card>
        <v-card-title>
          <v-icon class="mr-2">mdi-lock-reset</v-icon>
          Recuperar Senha
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-2 mb-4">
            Digite seu email para receber instruções de recuperação de senha.
          </p>
          
          <v-text-field
            v-model="forgotEmail"
            label="Email"
            type="email"
            prepend-inner-icon="mdi-email"
            variant="outlined"
          />
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="grey"
            variant="text"
            @click="showForgotPassword = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            @click="handleForgotPassword"
          >
            Enviar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const loading = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)
const showForgotPassword = ref(false)
const forgotEmail = ref('')
const generalError = ref('')

const loginForm = ref({
  username: '',
  password: ''
})

const errors = ref({
  username: '',
  password: ''
})

// Computed
const isFormValid = computed(() => {
  return loginForm.value.username.length > 0 && 
         loginForm.value.password.length > 0
})

// Methods
const clearError = (field: string) => {
  errors.value[field] = ''
  if (generalError.value) {
    generalError.value = ''
  }
}

const validateForm = () => {
  let isValid = true
  
  // Reset errors
  errors.value = {
    username: '',
    password: ''
  }
  
  // Validate username
  if (!loginForm.value.username) {
    errors.value.username = 'Usuário é obrigatório'
    isValid = false
  }
  
  // Validate password
  if (!loginForm.value.password) {
    errors.value.password = 'Senha é obrigatória'
    isValid = false
  } else if (loginForm.value.password.length < 3) {
    errors.value.password = 'Senha deve ter pelo menos 3 caracteres'
    isValid = false
  }
  
  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) {
    return
  }
  
  try {
    loading.value = true
    generalError.value = ''
    
    const success = await authStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password,
      rememberMe: rememberMe.value
    })
    
    if (success) {
      // Redirect to dashboard
      router.push('/')
    } else {
      generalError.value = 'Credenciais inválidas. Tente novamente.'
    }
  } catch (error) {
    console.error('Erro no login:', error)
    generalError.value = 'Erro interno. Tente novamente mais tarde.'
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = () => {
  // Simulate forgot password functionality
  alert(`Email de recuperação enviado para: ${forgotEmail.value}`)
  showForgotPassword.value = false
  forgotEmail.value = ''
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
}

.v-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}

@media (max-width: 600px) {
  .v-card {
    margin: 16px;
  }
}
</style>
