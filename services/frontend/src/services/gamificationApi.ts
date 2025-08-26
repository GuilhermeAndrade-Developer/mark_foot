/**
 * Gamification API Service
 * Handles all gamification-related API calls
 */

import api from './api'

export interface UserProfile {
  id: number
  user: number
  total_points: number
  level: number
  experience_points: number
  prediction_streak: number
  login_streak: number
  last_login_date: string | null
  is_public_profile: boolean
  allow_friend_requests: boolean
  favorite_team: number | null
  favorite_competition: number | null
  created_at: string
  updated_at: string
}

export interface Badge {
  id: number
  name: string
  description: string
  badge_type: 'prediction' | 'fantasy' | 'social' | 'streak' | 'special'
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'
  icon_url: string
  points_reward: number
  required_predictions?: number
  required_streak?: number
  required_fantasy_points?: number
  is_active: boolean
  created_at: string
}

export interface UserBadge {
  id: number
  user: number
  badge: Badge
  earned_at: string
  is_showcased: boolean
}

export interface PredictionGame {
  id: number
  name: string
  description: string
  game_type: 'match_result' | 'exact_score' | 'weekly_round' | 'tournament'
  status: 'upcoming' | 'active' | 'closed' | 'resolved'
  entry_fee_points: number
  reward_multiplier: number
  match?: number
  competition?: number
  starts_at: string
  ends_at: string
  created_at: string
}

export interface Prediction {
  id: number
  user: number
  game: PredictionGame
  prediction_data: any
  points_earned: number
  is_correct: boolean | null
  created_at: string
  resolved_at: string | null
}

export interface FantasyLeague {
  id: string
  name: string
  description: string
  league_type: 'public' | 'private' | 'premium'
  max_participants: number
  entry_fee_points: number
  prize_pool: number
  is_active: boolean
  join_code: string
  competition: number
  created_by: number
  season: number
  created_at: string
  starts_at: string
  ends_at: string
}

export interface FantasyTeam {
  id: string
  name: string
  formation: '4-4-2' | '4-3-3' | '3-5-2' | '4-5-1' | '5-3-2'
  total_points: number
  remaining_budget: number
  league: string
  owner: number
  goalkeepers: number[]
  defenders: number[]
  midfielders: number[]
  forwards: number[]
  created_at: string
  updated_at: string
}

export interface Challenge {
  id: number
  title: string
  description: string
  challenge_type: 'prediction' | 'fantasy' | 'streak' | 'social'
  status: 'upcoming' | 'active' | 'completed' | 'cancelled'
  requirements: any
  points_reward: number
  badge_reward?: Badge
  max_participants: number
  current_participants: number
  start_date: string
  end_date: string
  created_at: string
  is_active: boolean
}

export interface UserChallenge {
  id: number
  user: number
  challenge: Challenge
  status: 'participating' | 'completed' | 'failed'
  progress_data: any
  completion_percentage: number
  points_earned: number
  joined_at: string
  completed_at: string | null
}

export interface PointTransaction {
  id: number
  user: number
  transaction_type: 'earned' | 'spent' | 'bonus' | 'penalty' | 'refund'
  amount: number
  description: string
  source_type?: string
  source_id?: number
  balance_before: number
  balance_after: number
  created_at: string
}

export interface LeaderboardEntry {
  rank: number
  username: string
  total_points: number
  level: number
}

export interface DashboardStats {
  total_points: number
  level: number
  badges_count: number
  predictions_count: number
  challenges_completed: number
  fantasy_teams_count: number
  current_rank: number
}

class GamificationApiService {
  // User Profile
  async getUserProfile(): Promise<UserProfile> {
    const response = await api.get('/gamification/profiles/me/')
    return response.data
  }

  async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.patch('/gamification/profiles/me/', data)
    return response.data
  }

  // Badges
  async getBadges(): Promise<Badge[]> {
    const response = await api.get('/gamification/badges/')
    return response.data.results
  }

  async getUserBadges(): Promise<UserBadge[]> {
    const response = await api.get('/gamification/user-badges/my_badges/')
    return response.data
  }

  // Prediction Games
  async getPredictionGames(): Promise<PredictionGame[]> {
    const response = await api.get('/gamification/prediction-games/')
    return response.data.results
  }

  async getUserPredictions(): Promise<Prediction[]> {
    const response = await api.get('/gamification/predictions/my_predictions/')
    return response.data
  }

  async createPrediction(gameId: number, predictionData: any): Promise<Prediction> {
    const response = await api.post('/gamification/predictions/', {
      game: gameId,
      prediction_data: predictionData
    })
    return response.data
  }

  // Fantasy
  async getFantasyLeagues(): Promise<FantasyLeague[]> {
    const response = await api.get('/gamification/fantasy-leagues/')
    return response.data.results
  }

  async getUserFantasyTeams(): Promise<FantasyTeam[]> {
    const response = await api.get('/gamification/fantasy-teams/my_teams/')
    return response.data
  }

  async createFantasyTeam(teamData: Partial<FantasyTeam>): Promise<FantasyTeam> {
    const response = await api.post('/gamification/fantasy-teams/', teamData)
    return response.data
  }

  async joinFantasyLeague(leagueId: string, joinCode: string): Promise<any> {
    const response = await api.post(`/gamification/fantasy-leagues/${leagueId}/join/`, {
      join_code: joinCode
    })
    return response.data
  }

  // Challenges
  async getChallenges(): Promise<Challenge[]> {
    const response = await api.get('/gamification/challenges/')
    return response.data.results
  }

  async getUserChallenges(): Promise<UserChallenge[]> {
    const response = await api.get('/gamification/user-challenges/my_challenges/')
    return response.data
  }

  async joinChallenge(challengeId: number): Promise<UserChallenge> {
    const response = await api.post(`/gamification/challenges/${challengeId}/join/`)
    return response.data
  }

  // Points
  async getUserTransactions(): Promise<PointTransaction[]> {
    const response = await api.get('/gamification/transactions/my_transactions/')
    return response.data
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get('/gamification/dashboard/stats/')
    return response.data
  }

  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    const response = await api.get('/gamification/dashboard/leaderboard/')
    return response.data
  }

  // Admin methods
  async createPredictionGame(gameData: Partial<PredictionGame>): Promise<PredictionGame> {
    const response = await api.post('/gamification/prediction-games/', gameData)
    return response.data
  }

  async createChallenge(challengeData: Partial<Challenge>): Promise<Challenge> {
    const response = await api.post('/gamification/challenges/', challengeData)
    return response.data
  }

  async createBadge(badgeData: Partial<Badge>): Promise<Badge> {
    const response = await api.post('/gamification/badges/', badgeData)
    return response.data
  }

  async getAllUserProfiles(): Promise<UserProfile[]> {
    const response = await api.get('/gamification/profiles/')
    return response.data.results
  }

  async getAllBadges(): Promise<Badge[]> {
    const response = await api.get('/gamification/badges/')
    return response.data.results
  }

  async getAllChallenges(): Promise<Challenge[]> {
    const response = await api.get('/gamification/challenges/')
    return response.data.results
  }

  async getAllPredictionGames(): Promise<PredictionGame[]> {
    const response = await api.get('/gamification/prediction-games/')
    return response.data.results
  }
}

export default new GamificationApiService()
