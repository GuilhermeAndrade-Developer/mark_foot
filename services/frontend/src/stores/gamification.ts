import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import gamificationApi, { 
  UserProfile, 
  Badge, 
  PredictionGame, 
  Challenge, 
  FantasyLeague, 
  UserFantasyTeam,
  PointTransaction,
  DashboardStats 
} from '../services/gamificationApi'

export const useGamificationStore = defineStore('gamification', () => {
  // State
  const userProfile = ref<UserProfile | null>(null)
  const badges = ref<Badge[]>([])
  const userBadges = ref<Badge[]>([])
  const predictionGames = ref<PredictionGame[]>([])
  const userPredictions = ref<any[]>([])
  const fantasyLeagues = ref<FantasyLeague[]>([])
  const userFantasyTeams = ref<UserFantasyTeam[]>([])
  const challenges = ref<Challenge[]>([])
  const userChallenges = ref<any[]>([])
  const pointTransactions = ref<PointTransaction[]>([])
  const dashboardStats = ref<DashboardStats | null>(null)
  const leaderboard = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const availableBadges = computed(() => 
    badges.value.filter(badge => !userBadges.value.some(ub => ub.id === badge.id))
  )

  const earnedBadges = computed(() => userBadges.value)

  const activePredictionGames = computed(() => 
    predictionGames.value.filter(game => game.status === 'active')
  )

  const activeChallenges = computed(() => 
    challenges.value.filter(challenge => challenge.status === 'active')
  )

  const userActiveChallenges = computed(() => 
    userChallenges.value.filter(uc => uc.status === 'active')
  )

  const recentTransactions = computed(() => 
    pointTransactions.value.slice(0, 10)
  )

  const userLevel = computed(() => userProfile.value?.level || 1)
  const userPoints = computed(() => userProfile.value?.total_points || 0)
  const userStreak = computed(() => userProfile.value?.prediction_streak || 0)

  // Actions
  async function loadUserProfile() {
    try {
      const profile = await gamificationApi.getUserProfile()
      userProfile.value = profile
      return profile
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar perfil do usuário'
      throw err
    }
  }

  async function loadBadges() {
    try {
      badges.value = await gamificationApi.getBadges()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar badges'
      throw err
    }
  }

  async function loadUserBadges() {
    try {
      userBadges.value = await gamificationApi.getUserBadges()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar badges do usuário'
      throw err
    }
  }

  async function loadPredictionGames() {
    try {
      predictionGames.value = await gamificationApi.getPredictionGames()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar jogos de predição'
      throw err
    }
  }

  async function loadUserPredictions() {
    try {
      userPredictions.value = await gamificationApi.getUserPredictions()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar predições do usuário'
      throw err
    }
  }

  async function loadFantasyLeagues() {
    try {
      fantasyLeagues.value = await gamificationApi.getFantasyLeagues()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar ligas de fantasy'
      throw err
    }
  }

  async function loadUserFantasyTeams() {
    try {
      userFantasyTeams.value = await gamificationApi.getUserFantasyTeams()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar times de fantasy do usuário'
      throw err
    }
  }

  async function loadChallenges() {
    try {
      challenges.value = await gamificationApi.getChallenges()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar desafios'
      throw err
    }
  }

  async function loadUserChallenges() {
    try {
      userChallenges.value = await gamificationApi.getUserChallenges()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar desafios do usuário'
      throw err
    }
  }

  async function loadPointTransactions() {
    try {
      pointTransactions.value = await gamificationApi.getPointTransactions()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar transações de pontos'
      throw err
    }
  }

  async function loadDashboardStats() {
    try {
      dashboardStats.value = await gamificationApi.getDashboardStats()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar estatísticas do dashboard'
      throw err
    }
  }

  async function loadLeaderboard() {
    try {
      leaderboard.value = await gamificationApi.getLeaderboard()
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar leaderboard'
      throw err
    }
  }

  async function createPrediction(predictionData: any) {
    try {
      const response = await gamificationApi.createPrediction(predictionData)
      await loadUserPredictions()
      await loadUserProfile()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar predição'
      throw err
    }
  }

  async function joinChallenge(challengeId: number) {
    try {
      const response = await gamificationApi.joinChallenge(challengeId)
      await loadUserChallenges()
      await loadUserProfile()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao participar do desafio'
      throw err
    }
  }

  async function createFantasyTeam(teamData: any) {
    try {
      const response = await gamificationApi.createFantasyTeam(teamData)
      await loadUserFantasyTeams()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar time de fantasy'
      throw err
    }
  }

  async function updateUserProfile(profileData: Partial<UserProfile>) {
    try {
      const response = await gamificationApi.updateUserProfile(profileData)
      userProfile.value = response
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao atualizar perfil'
      throw err
    }
  }

  // Initialize gamification data
  async function initializeGamification() {
    try {
      loading.value = true
      await Promise.all([
        loadUserProfile(),
        loadDashboardStats(),
        loadBadges(),
        loadUserBadges(),
        loadChallenges(),
        loadUserChallenges(),
        loadPredictionGames(),
        loadUserPredictions(),
        loadLeaderboard()
      ])
    } catch (err: any) {
      error.value = err.message || 'Erro ao inicializar gamificação'
      console.error('Error initializing gamification:', err)
    } finally {
      loading.value = false
    }
  }

  // Admin methods for creating content
  async function createPredictionGame(gameData: any) {
    try {
      const response = await gamificationApi.createPredictionGame(gameData)
      predictionGames.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar jogo de predição'
      throw err
    }
  }

  async function createChallenge(challengeData: any) {
    try {
      const response = await gamificationApi.createChallenge(challengeData)
      challenges.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar desafio'
      throw err
    }
  }

  async function createBadge(badgeData: any) {
    try {
      const response = await gamificationApi.createBadge(badgeData)
      badges.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao criar badge'
      throw err
    }
  }

  // Admin methods for user management
  async function getUserProfiles() {
    try {
      const response = await gamificationApi.getAllUserProfiles()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar perfis de usuários'
      throw err
    }
  }

  async function getAllBadgesAdmin() {
    try {
      const response = await gamificationApi.getAllBadges()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erro ao carregar badges'
      throw err
    }
  }

  // Clear all state (for logout)
  function clearGamificationState() {
    userProfile.value = null
    badges.value = []
    userBadges.value = []
    predictionGames.value = []
    userPredictions.value = []
    fantasyLeagues.value = []
    userFantasyTeams.value = []
    challenges.value = []
    userChallenges.value = []
    pointTransactions.value = []
    dashboardStats.value = null
    leaderboard.value = []
    error.value = null
  }

  return {
    // State
    userProfile,
    badges,
    userBadges,
    predictionGames,
    userPredictions,
    fantasyLeagues,
    userFantasyTeams,
    challenges,
    userChallenges,
    pointTransactions,
    dashboardStats,
    leaderboard,
    loading,
    error,

    // Computed
    availableBadges,
    earnedBadges,
    activePredictionGames,
    activeChallenges,
    userActiveChallenges,
    recentTransactions,
    userLevel,
    userPoints,
    userStreak,

    // Actions
    loadUserProfile,
    loadBadges,
    loadUserBadges,
    loadPredictionGames,
    loadUserPredictions,
    loadFantasyLeagues,
    loadUserFantasyTeams,
    loadChallenges,
    loadUserChallenges,
    loadPointTransactions,
    loadDashboardStats,
    loadLeaderboard,
    createPrediction,
    joinChallenge,
    createFantasyTeam,
    updateUserProfile,
    initializeGamification,
    clearGamificationState,

    // Admin actions
    createPredictionGame,
    createChallenge,
    createBadge,
    getUserProfiles,
    getAllBadgesAdmin
  }
})

