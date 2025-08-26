import api from './api'

export interface SyncOptions {
  competitions: string[]
  includeStandings: boolean
  includePlayers: boolean
}

export interface SyncProgress {
  current: number
  total: number
}

export interface SyncLog {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  timestamp: Date
}

export interface ApiStatus {
  name: string
  status: 'online' | 'offline' | 'error'
  rateLimit: string
  lastCheck: string
  error?: string
}

export interface DatabaseStats {
  competitions: number
  teams: number
  players: number
  matches: number
  standings: number
  apiLogs: number
  recentSyncs: number
  activePlayers: number
}

class SyncService {
  /**
   * Get database statistics summary
   */
  async getStats(): Promise<DatabaseStats> {
    try {
      const response = await api.get('/stats/summary/')
      return response.data
    } catch (error) {
      console.error('Error fetching stats:', error)
      throw error
    }
  }

  /**
   * Sync a specific competition
   */
  async syncCompetition(competitionCode: string, includeStandings = true): Promise<any> {
    try {
      const response = await api.post('/sync/competition/', {
        competition_code: competitionCode,
        include_standings: includeStandings
      })
      return response.data
    } catch (error) {
      console.error(`Error syncing competition ${competitionCode}:`, error)
      throw error
    }
  }

  /**
   * Sync players for a specific competition
   */
  async syncPlayers(competitionCode: string, limit = 10): Promise<any> {
    try {
      const response = await api.post('/sync/players/', {
        competition_code: competitionCode,
        limit
      })
      return response.data
    } catch (error) {
      console.error(`Error syncing players for ${competitionCode}:`, error)
      throw error
    }
  }

  /**
   * Sync player photos from TheSportsDB
   */
  async syncPlayerPhotos(limit = 50, dryRun = false): Promise<any> {
    try {
      const response = await api.post('/sync/player-photos/', {
        limit,
        dry_run: dryRun
      })
      return response.data
    } catch (error) {
      console.error('Error syncing player photos:', error)
      throw error
    }
  }

  /**
   * Check status of external APIs
   */
  async checkApiStatus(): Promise<ApiStatus[]> {
    try {
      const response = await api.get('/sync/api-status/')
      return response.data.apis || []
    } catch (error) {
      console.error('Error checking API status:', error)
      throw error
    }
  }

  /**
   * Get recent sync logs
   */
  async getSyncLogs(limit = 50): Promise<any[]> {
    try {
      const response = await api.get(`/sync/logs/?limit=${limit}`)
      return response.data.logs || []
    } catch (error) {
      console.error('Error fetching sync logs:', error)
      throw error
    }
  }

  /**
   * Execute full synchronization with rate limiting
   */
  async executeFullSync(
    options: SyncOptions,
    onProgress?: (progress: SyncProgress) => void,
    onLog?: (log: SyncLog) => void,
    abortSignal?: AbortSignal
  ): Promise<boolean> {
    const { competitions, includeStandings, includePlayers } = options
    let currentStep = 0
    const totalSteps = competitions.length * (includeStandings ? 3 : 2) + (includePlayers ? competitions.length : 0)
    
    // Clear any existing auth tokens to avoid 401 errors
    localStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_token')
    
    const updateProgress = () => {
      if (onProgress) {
        onProgress({ current: currentStep, total: totalSteps })
      }
    }

    const addLog = (type: SyncLog['type'], message: string) => {
      if (onLog) {
        onLog({ type, message, timestamp: new Date() })
      }
    }

    try {
      addLog('info', '🚀 Iniciando sincronização completa...')
      updateProgress()

      for (const competitionCode of competitions) {
        // Check if aborted
        if (abortSignal?.aborted) {
          addLog('warning', '⚠️ Sincronização cancelada pelo usuário')
          return false
        }

        try {
          // Sync competition (teams, matches, standings)
          addLog('info', `📊 Sincronizando ${competitionCode}...`)
          
          const competitionResult = await this.syncCompetition(competitionCode, includeStandings)
          
          if (competitionResult.success) {
            addLog('success', `✅ ${competitionCode}: ${competitionResult.summary}`)
          } else {
            addLog('error', `❌ Erro em ${competitionCode}: ${competitionResult.error}`)
          }
          
          currentStep++
          updateProgress()

          // Rate limiting - wait between competitions
          addLog('info', `⏳ Aguardando rate limit (6 segundos)...`)
          await this.sleep(6000)

          // Sync players if enabled
          if (includePlayers) {
            if (abortSignal?.aborted) break

            addLog('info', `👥 Sincronizando jogadores de ${competitionCode}...`)
            
            try {
              const playersResult = await this.syncPlayers(competitionCode, 15) // Limit to 15 teams
              
              if (playersResult.success) {
                addLog('success', `✅ Jogadores de ${competitionCode}: ${playersResult.summary}`)
              } else {
                addLog('error', `❌ Erro nos jogadores de ${competitionCode}: ${playersResult.error}`)
              }
            } catch (error: any) {
              addLog('error', `❌ Erro nos jogadores de ${competitionCode}: ${error.message}`)
            }
            
            currentStep++
            updateProgress()

            // Rate limiting for players
            addLog('info', `⏳ Aguardando rate limit (3 segundos)...`)
            await this.sleep(3000)
          }

        } catch (error: any) {
          addLog('error', `❌ Erro em ${competitionCode}: ${error.message}`)
          currentStep++
          updateProgress()
        }
      }

      if (!abortSignal?.aborted) {
        addLog('success', '🎉 Sincronização completa finalizada!')
        return true
      }

      return false

    } catch (error: any) {
      addLog('error', `❌ Erro na sincronização: ${error.message}`)
      return false
    }
  }

  /**
   * Helper method to sleep for a given time
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Get available competitions for sync
   */
  getAvailableCompetitions() {
    return [
      { code: 'PL', name: 'Premier League' },
      { code: 'BL1', name: 'Bundesliga' },
      { code: 'PD', name: 'Primera División' },
      { code: 'SA', name: 'Serie A' },
      { code: 'FL1', name: 'Ligue 1' },
      { code: 'BSA', name: 'Brasileirão' },
      { code: 'CL', name: 'Champions League' },
      { code: 'DED', name: 'Eredivisie' },
      { code: 'PPL', name: 'Primeira Liga' }
    ]
  }
}

export const syncService = new SyncService()
