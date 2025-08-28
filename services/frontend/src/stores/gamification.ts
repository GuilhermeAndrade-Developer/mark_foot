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

// ============ MOCK DATA FOR DEMO ============
const MOCK_USER_PROFILE: UserProfile = {
  id: 1,
  user: 1,
  total_points: 1250,
  level: 8,
  experience_points: 2400,
  prediction_streak: 12,
  login_streak: 7,
  last_login_date: new Date().toISOString(),
  is_public_profile: true,
  allow_friend_requests: true,
  favorite_team: 1,
  favorite_competition: 1,
  created_at: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
  updated_at: new Date().toISOString()
}

const MOCK_DASHBOARD_STATS: DashboardStats = {
  total_points: 1250,
  level: 8,
  badges_count: 7,
  predictions_count: 34,
  challenges_completed: 15,
  fantasy_teams_count: 3,
  current_rank: 23
}

const MOCK_BADGES: Badge[] = [
  {
    id: 1,
    name: 'Primeiro Passo',
    description: 'Faça sua primeira predição',
    badge_type: 'prediction',
    rarity: 'common',
    icon_url: '/badges/first-prediction.png',
    points_reward: 50,
    required_predictions: 1,
    is_active: true,
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    name: 'Vidente',
    description: 'Acerte 10 predições seguidas',
    badge_type: 'streak',
    rarity: 'rare',
    icon_url: '/badges/prophet.png',
    points_reward: 200,
    required_streak: 10,
    is_active: true,
    created_at: new Date().toISOString()
  }
]

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
      console.log('API de gamificação não disponível, usando dados de demonstração')
      userProfile.value = MOCK_USER_PROFILE
      return MOCK_USER_PROFILE
    }
  }

  async function loadBadges() {
    try {
      badges.value = await gamificationApi.getBadges()
    } catch (err: any) {
      console.log('API de badges não disponível, usando dados de demonstração')
      badges.value = MOCK_BADGES
    }
  }

  async function loadUserBadges() {
    try {
      userBadges.value = await gamificationApi.getUserBadges()
    } catch (err: any) {
      console.log('API de user badges não disponível, usando dados de demonstração')
      userBadges.value = MOCK_BADGES // Simulando que o usuário tem esses badges
    }
  }

  async function loadPredictionGames() {
    try {
      predictionGames.value = await gamificationApi.getPredictionGames()
    } catch (err: any) {
      console.log('API de prediction games não disponível, usando dados de demonstração')
      predictionGames.value = []
    }
  }

  async function loadUserPredictions() {
    try {
      userPredictions.value = await gamificationApi.getUserPredictions()
    } catch (err: any) {
      console.log('API de user predictions não disponível, usando dados de demonstração')
      userPredictions.value = []
    }
  }

  async function loadFantasyLeagues() {
    try {
      fantasyLeagues.value = await gamificationApi.getFantasyLeagues()
    } catch (err: any) {
      console.log('API de fantasy leagues não disponível, usando dados de demonstração')
      fantasyLeagues.value = []
    }
  }

  async function loadUserFantasyTeams() {
    try {
      userFantasyTeams.value = await gamificationApi.getUserFantasyTeams()
    } catch (err: any) {
      console.log('API de user fantasy teams não disponível, usando dados de demonstração')
      userFantasyTeams.value = []
    }
  }

  async function loadChallenges() {
    try {
      challenges.value = await gamificationApi.getChallenges()
    } catch (err: any) {
      console.log('API de challenges não disponível, usando dados de demonstração')
      challenges.value = []
    }
  }

  async function loadUserChallenges() {
    try {
      userChallenges.value = await gamificationApi.getUserChallenges()
    } catch (err: any) {
      console.log('API de user challenges não disponível, usando dados de demonstração')
      userChallenges.value = []
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
      console.log('API de dashboard stats não disponível, usando dados de demonstração')
      dashboardStats.value = MOCK_DASHBOARD_STATS
    }
  }

  async function loadLeaderboard() {
    try {
      leaderboard.value = await gamificationApi.getLeaderboard()
    } catch (err: any) {
      console.log('API de leaderboard não disponível, usando dados de demonstração')
      leaderboard.value = [
        { username: 'João Silva', points: 3450, rank: 1 },
        { username: 'Maria Santos', points: 3200, rank: 2 },
        { username: 'Pedro Costa', points: 2980, rank: 3 },
        { username: 'Ana Oliveira', points: 2750, rank: 4 },
        { username: 'Carlos Lima', points: 2500, rank: 5 }
      ]
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

