"""
Seeder for gamification module data.
Creates professional development data for badges, challenges, etc.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gamification.models import (
    UserProfile, Badge, UserBadge, Challenge, UserChallenge,
    PointTransaction, Leaderboard, LeaderboardEntry
)
from django.utils import timezone
from datetime import timedelta, date
import random


class Command(BaseCommand):
    help = 'Seed gamification data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create gamification data for',
        )

    def handle(self, *args, **options):
        self.stdout.write('🎮 Seeding gamification data...')
        
        users_limit = options['users']
        
        # Create user profiles
        profiles_created = self.create_user_profiles(users_limit)
        
        # Create badges
        badges_created = self.create_badges()
        
        # Award badges
        badges_awarded = self.award_badges()
        
        # Create challenges
        challenges_created = self.create_challenges()
        
        # Create leaderboards
        leaderboards_created = self.create_leaderboards()
        
        # Create transactions
        transactions_created = self.create_transactions()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Gamification data seeded:\n'
                f'   👤 User Profiles: {profiles_created}\n'
                f'   🏅 Badges: {badges_created}\n'
                f'   🎖️  Badges Awarded: {badges_awarded}\n'
                f'   🎯 Challenges: {challenges_created}\n'
                f'   🏆 Leaderboards: {leaderboards_created}\n'
                f'   💰 Transactions: {transactions_created}'
            )
        )

    def create_user_profiles(self, users_limit):
        """Create user profiles for gamification"""
        users = User.objects.filter(is_active=True)[:users_limit]
        created_count = 0

        for user in users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'total_points': random.randint(100, 2000),
                    'level': random.randint(1, 15),
                    'experience_points': random.randint(0, 1000),
                    'prediction_streak': random.randint(0, 15),
                    'max_prediction_streak': random.randint(0, 20),
                    'login_streak': random.randint(0, 45),
                    'max_login_streak': random.randint(0, 60),
                    'total_predictions': random.randint(10, 200),
                    'correct_predictions': random.randint(5, 150),
                    'fantasy_points': random.randint(0, 500),
                    'social_interactions': random.randint(0, 100),
                    'achievements_unlocked': random.randint(1, 10)
                }
            )
            if created:
                created_count += 1

        return created_count

    def create_badges(self):
        """Create system badges"""
        badges_data = [
            {
                'name': 'NOVATO',
                'description': 'Bem-vindo ao Mark Foot!',
                'badge_type': 'MILESTONE',
                'rarity': 'COMMON',
                'points_reward': 10,
                'icon': 'mdi-star',
                'color': '#4CAF50',
                'is_active': True
            },
            {
                'name': 'PREDITOR_INICIANTE',
                'description': 'Faça sua primeira previsão correta',
                'badge_type': 'PREDICTION',
                'rarity': 'COMMON',
                'points_reward': 25,
                'required_predictions': 1,
                'icon': 'mdi-crystal-ball',
                'color': '#2196F3',
                'is_active': True
            },
            {
                'name': 'PREDITOR_EXPERIENTE',
                'description': 'Acerte 10 previsões',
                'badge_type': 'PREDICTION',
                'rarity': 'RARE',
                'points_reward': 100,
                'required_predictions': 10,
                'icon': 'mdi-crystal-ball',
                'color': '#FF9800',
                'is_active': True
            },
            {
                'name': 'VIDENTE',
                'description': 'Acerte 50 previsões',
                'badge_type': 'PREDICTION',
                'rarity': 'EPIC',
                'points_reward': 500,
                'required_predictions': 50,
                'icon': 'mdi-eye',
                'color': '#9C27B0',
                'is_active': True
            },
            {
                'name': 'SOCIALITE',
                'description': 'Interaja 25 vezes nas redes sociais',
                'badge_type': 'SOCIAL',
                'rarity': 'RARE',
                'points_reward': 75,
                'required_social_interactions': 25,
                'icon': 'mdi-account-group',
                'color': '#E91E63',
                'is_active': True
            },
            {
                'name': 'USUARIO_FIEL',
                'description': 'Faça login por 7 dias consecutivos',
                'badge_type': 'ENGAGEMENT',
                'rarity': 'RARE',
                'points_reward': 150,
                'required_streak': 7,
                'icon': 'mdi-calendar-check',
                'color': '#607D8B',
                'is_active': True
            },
            {
                'name': 'DEDICADO',
                'description': 'Faça login por 30 dias consecutivos',
                'badge_type': 'ENGAGEMENT',
                'rarity': 'EPIC',
                'points_reward': 500,
                'required_streak': 30,
                'icon': 'mdi-fire',
                'color': '#FF5722',
                'is_active': True
            },
            {
                'name': 'GESTOR_FANTASY',
                'description': 'Pontue 100 pontos no fantasy',
                'badge_type': 'FANTASY',
                'rarity': 'RARE',
                'points_reward': 200,
                'required_fantasy_points': 100,
                'icon': 'mdi-trophy',
                'color': '#FFC107',
                'is_active': True
            },
            {
                'name': 'MESTRE_FANTASY',
                'description': 'Pontue 500 pontos no fantasy',
                'badge_type': 'FANTASY',
                'rarity': 'LEGENDARY',
                'points_reward': 1000,
                'required_fantasy_points': 500,
                'icon': 'mdi-crown',
                'color': '#FFD700',
                'is_active': True
            },
            {
                'name': 'CONTRIBUIDOR',
                'description': 'Complete seu primeiro desafio',
                'badge_type': 'CHALLENGE',
                'rarity': 'COMMON',
                'points_reward': 50,
                'icon': 'mdi-flag-checkered',
                'color': '#795548',
                'is_active': True
            }
        ]

        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1

        return created_count

    def award_badges(self):
        """Award badges to users based on their activity"""
        users = User.objects.filter(is_active=True)
        badges = Badge.objects.filter(is_active=True)
        created_count = 0

        for user in users:
            profile = UserProfile.objects.filter(user=user).first()
            if not profile:
                continue

            # Award badges based on user activity
            eligible_badges = []

            # Novato badge for everyone
            if badges.filter(name='NOVATO').exists():
                eligible_badges.append(badges.get(name='NOVATO'))

            # Prediction badges
            if profile.correct_predictions >= 1 and badges.filter(name='PREDITOR_INICIANTE').exists():
                eligible_badges.append(badges.get(name='PREDITOR_INICIANTE'))
            
            if profile.correct_predictions >= 10 and badges.filter(name='PREDITOR_EXPERIENTE').exists():
                eligible_badges.append(badges.get(name='PREDITOR_EXPERIENTE'))
            
            if profile.correct_predictions >= 50 and badges.filter(name='VIDENTE').exists():
                eligible_badges.append(badges.get(name='VIDENTE'))

            # Social badges
            if profile.social_interactions >= 25 and badges.filter(name='SOCIALITE').exists():
                eligible_badges.append(badges.get(name='SOCIALITE'))

            # Engagement badges
            if profile.max_login_streak >= 7 and badges.filter(name='USUARIO_FIEL').exists():
                eligible_badges.append(badges.get(name='USUARIO_FIEL'))
            
            if profile.max_login_streak >= 30 and badges.filter(name='DEDICADO').exists():
                eligible_badges.append(badges.get(name='DEDICADO'))

            # Fantasy badges
            if profile.fantasy_points >= 100 and badges.filter(name='GESTOR_FANTASY').exists():
                eligible_badges.append(badges.get(name='GESTOR_FANTASY'))
            
            if profile.fantasy_points >= 500 and badges.filter(name='MESTRE_FANTASY').exists():
                eligible_badges.append(badges.get(name='MESTRE_FANTASY'))

            # Award eligible badges
            for badge in eligible_badges:
                user_badge, created = UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge,
                    defaults={
                        'earned_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                        'is_showcased': random.choice([True, False])
                    }
                )
                if created:
                    created_count += 1

        return created_count

    def create_challenges(self):
        """Create system challenges"""
        challenges_data = [
            {
                'title': 'Preditor Semanal',
                'description': 'Faça 5 previsões esta semana',
                'challenge_type': 'WEEKLY',
                'status': 'ACTIVE',
                'requirements': {'target_predictions': 5},
                'points_reward': 100,
                'max_participants': 1000,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=7)
            },
            {
                'title': 'Gestor Fantasy',
                'description': 'Atualize seu time fantasy',
                'challenge_type': 'WEEKLY',
                'status': 'ACTIVE',
                'requirements': {'target_fantasy_updates': 1},
                'points_reward': 50,
                'max_participants': 500,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=7)
            },
            {
                'title': 'Social Butterfly',
                'description': 'Faça 10 interações sociais',
                'challenge_type': 'MONTHLY',
                'status': 'ACTIVE',
                'requirements': {'target_social_interactions': 10},
                'points_reward': 200,
                'max_participants': 800,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=30)
            },
            {
                'title': 'Login Diário',
                'description': 'Faça login todos os dias desta semana',
                'challenge_type': 'DAILY',
                'status': 'ACTIVE',
                'requirements': {'target_login_streak': 7},
                'points_reward': 150,
                'max_participants': 2000,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=7)
            },
            {
                'title': 'Explorador de Conteúdo',
                'description': 'Leia 3 artigos esta semana',
                'challenge_type': 'WEEKLY',
                'status': 'ACTIVE',
                'requirements': {'target_articles_read': 3},
                'points_reward': 75,
                'max_participants': 1500,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=7)
            }
        ]

        created_count = 0
        for challenge_data in challenges_data:
            challenge, created = Challenge.objects.get_or_create(
                title=challenge_data['title'],
                defaults=challenge_data
            )
            if created:
                created_count += 1

        return created_count

    def create_leaderboards(self):
        """Create system leaderboards"""
        leaderboards_data = [
            {
                'name': 'previsoes_semanais',
                'leaderboard_type': 'WEEKLY',
                'description': 'Melhores preditores da semana',
                'is_active': True,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=7)
            },
            {
                'name': 'fantasy_mensal',
                'leaderboard_type': 'MONTHLY',
                'description': 'Ranking fantasy do mês',
                'is_active': True,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=30)
            },
            {
                'name': 'pontos_gerais',
                'leaderboard_type': 'ALL_TIME',
                'description': 'Ranking geral de pontos',
                'is_active': True,
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=365)
            }
        ]

        created_count = 0
        for lb_data in leaderboards_data:
            leaderboard, created = Leaderboard.objects.get_or_create(
                name=lb_data['name'],
                defaults=lb_data
            )
            if created:
                created_count += 1
                
                # Add entries for users
                users_with_profiles = User.objects.filter(
                    userprofile__isnull=False,
                    is_active=True
                ).order_by('-userprofile__total_points')[:10]
                
                for rank, user in enumerate(users_with_profiles, 1):
                    LeaderboardEntry.objects.create(
                        user=user,
                        leaderboard=leaderboard,
                        rank=rank,
                        score=user.userprofile.total_points,
                        additional_data={
                            'predictions': user.userprofile.total_predictions,
                            'level': user.userprofile.level
                        }
                    )

        return created_count

    def create_transactions(self):
        """Create point transactions"""
        users_with_profiles = User.objects.filter(userprofile__isnull=False, is_active=True)
        transaction_types = [
            'prediction_correct', 'prediction_bonus', 'challenge_completed', 
            'badge_earned', 'fantasy_win', 'daily_login', 'social_interaction'
        ]
        
        created_count = 0
        
        for user in users_with_profiles:
            # Create 10-25 transactions per user
            transaction_count = random.randint(10, 25)
            
            for _ in range(transaction_count):
                transaction_type = random.choice(transaction_types)
                points = random.randint(5, 100)
                
                PointTransaction.objects.create(
                    user=user,
                    transaction_type=transaction_type,
                    points=points,
                    description=f'Pontos por {transaction_type.replace("_", " ")}',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60))
                )
                created_count += 1

        return created_count
