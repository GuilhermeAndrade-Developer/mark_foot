<template>
  <div v-if="userProfile" class="user-progress-widget">
    <v-card variant="outlined" class="pa-3">
      <div class="d-flex align-center mb-2">
        <v-avatar size="32" color="primary" variant="tonal" class="mr-3">
          <span class="text-caption font-weight-bold">{{ userLevel }}</span>
        </v-avatar>
        <div class="flex-grow-1">
          <div class="d-flex justify-space-between">
            <span class="text-caption font-weight-bold">Nível {{ userLevel }}</span>
            <span class="text-caption">{{ userPoints }} pts</span>
          </div>
          <v-progress-linear
            :model-value="levelProgress"
            height="6"
            color="primary"
            rounded
            class="mt-1"
          />
        </div>
      </div>
      
      <div class="d-flex justify-space-around text-center">
        <div>
          <div class="text-caption font-weight-bold">{{ userStreak }}</div>
          <div class="text-caption text-medium-emphasis">Sequência</div>
        </div>
        <div>
          <div class="text-caption font-weight-bold">{{ badgesCount }}</div>
          <div class="text-caption text-medium-emphasis">Badges</div>
        </div>
        <div>
          <div class="text-caption font-weight-bold">#{{ userRank }}</div>
          <div class="text-caption text-medium-emphasis">Ranking</div>
        </div>
      </div>

      <v-btn
        v-if="activeChallengesCount > 0"
        size="small"
        color="success"
        variant="tonal"
        block
        class="mt-2"
        @click="$router.push('/gamification/challenges')"
      >
        <v-icon start size="16">mdi-target</v-icon>
        {{ activeChallengesCount }} Desafio{{ activeChallengesCount > 1 ? 's' : '' }} Ativo{{ activeChallengesCount > 1 ? 's' : '' }}
      </v-btn>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGamificationStore } from '@/stores/gamification'

const gamificationStore = useGamificationStore()

// Computed
const userProfile = computed(() => gamificationStore.userProfile)
const userLevel = computed(() => gamificationStore.userLevel)
const userPoints = computed(() => gamificationStore.userPoints)
const userStreak = computed(() => gamificationStore.userStreak)
const badgesCount = computed(() => gamificationStore.earnedBadges.length)
const activeChallengesCount = computed(() => gamificationStore.userActiveChallenges.length)
const userRank = computed(() => gamificationStore.dashboardStats?.current_rank || '-')

// Calculate level progress (assuming each level requires level * 1000 points)
const levelProgress = computed(() => {
  if (!userProfile.value) return 0
  
  const currentLevelPoints = userLevel.value * 1000
  const nextLevelPoints = (userLevel.value + 1) * 1000
  const pointsInCurrentLevel = userPoints.value - currentLevelPoints
  const pointsNeededForLevel = nextLevelPoints - currentLevelPoints
  
  return Math.min((pointsInCurrentLevel / pointsNeededForLevel) * 100, 100)
})
</script>

<style scoped>
.user-progress-widget {
  min-width: 200px;
}
</style>
