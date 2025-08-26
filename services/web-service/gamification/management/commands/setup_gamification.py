"""
Management command to create initial gamification data for testing.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

from gamification.models import (
    UserProfile, Badge, PredictionGame, Challenge, FantasyLeague
)
from core.models import Competition, Team, Season


class Command(BaseCommand):
    help = 'Create initial gamification data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all gamification data before creating new data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting gamification data...')
            UserProfile.objects.all().delete()
            Badge.objects.all().delete()
            PredictionGame.objects.all().delete()
            Challenge.objects.all().delete()
            FantasyLeague.objects.all().delete()

        # Create badges
        self.create_badges()
        
        # Create prediction games
        self.create_prediction_games()
        
        # Create challenges
        self.create_challenges()
        
        # Create fantasy leagues
        self.create_fantasy_leagues()
        
        # Create user profiles for existing users
        self.create_user_profiles()

        self.stdout.write(
            self.style.SUCCESS('Successfully created gamification data!')
        )

    def create_badges(self):
        """Create sample badges"""
        badges_data = [
            {
                'name': 'Primeira Predição',
                'description': 'Faça sua primeira predição',
                'badge_type': 'prediction',
                'rarity': 'common',
                'icon_url': 'https://example.com/badges/first-prediction.png',
                'points_reward': 50,
                'required_predictions': 1
            },
            {
                'name': 'Vidente',
                'description': 'Acerte 10 predições consecutivas',
                'badge_type': 'prediction',
                'rarity': 'rare',
                'icon_url': 'https://example.com/badges/prophet.png',
                'points_reward': 500,
                'required_streak': 10
            },
            {
                'name': 'Estrategista',
                'description': 'Monte seu primeiro time fantasy',
                'badge_type': 'fantasy',
                'rarity': 'common',
                'icon_url': 'https://example.com/badges/strategist.png',
                'points_reward': 100
            },
            {
                'name': 'Sequência de Fogo',
                'description': 'Mantenha uma sequência de 5 dias consecutivos',
                'badge_type': 'streak',
                'rarity': 'uncommon',
                'icon_url': 'https://example.com/badges/fire-streak.png',
                'points_reward': 200,
                'required_streak': 5
            },
            {
                'name': 'Lenda do Futebol',
                'description': 'Alcance 10.000 pontos',
                'badge_type': 'special',
                'rarity': 'legendary',
                'icon_url': 'https://example.com/badges/football-legend.png',
                'points_reward': 1000
            }
        ]

        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(f'Created badge: {badge.name}')

    def create_prediction_games(self):
        """Create sample prediction games"""
        prediction_games_data = [
            {
                'name': 'Resultado da Próxima Rodada',
                'description': 'Preveja o resultado das partidas da próxima rodada',
                'game_type': 'match_result',
                'status': 'active',
                'entry_fee_points': 10,
                'reward_multiplier': 2.0,
                'starts_at': timezone.now(),
                'ends_at': timezone.now() + timedelta(days=7)
            },
            {
                'name': 'Placar Exato - Final de Semana',
                'description': 'Acerte o placar exato das partidas do final de semana',
                'game_type': 'exact_score',
                'status': 'active',
                'entry_fee_points': 25,
                'reward_multiplier': 5.0,
                'starts_at': timezone.now(),
                'ends_at': timezone.now() + timedelta(days=3)
            },
            {
                'name': 'Desafio Semanal',
                'description': 'Complete todas as predições da semana',
                'game_type': 'weekly_round',
                'status': 'upcoming',
                'entry_fee_points': 50,
                'reward_multiplier': 3.0,
                'starts_at': timezone.now() + timedelta(days=1),
                'ends_at': timezone.now() + timedelta(days=8)
            }
        ]

        for game_data in prediction_games_data:
            game, created = PredictionGame.objects.get_or_create(
                name=game_data['name'],
                defaults=game_data
            )
            if created:
                self.stdout.write(f'Created prediction game: {game.name}')

    def create_challenges(self):
        """Create sample challenges"""
        challenges_data = [
            {
                'title': 'Novato das Predições',
                'description': 'Faça 5 predições para completar este desafio',
                'challenge_type': 'prediction',
                'status': 'active',
                'requirements': {'predictions_count': 5},
                'points_reward': 100,
                'max_participants': 1000,
                'start_date': timezone.now() - timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=30),
                'is_active': True
            },
            {
                'title': 'Mestre do Fantasy',
                'description': 'Monte um time fantasy e acumule 500 pontos',
                'challenge_type': 'fantasy',
                'status': 'active',
                'requirements': {'fantasy_points': 500},
                'points_reward': 250,
                'max_participants': 500,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=60),
                'is_active': True
            },
            {
                'title': 'Sequência Dourada',
                'description': 'Mantenha uma sequência de login de 7 dias',
                'challenge_type': 'streak',
                'status': 'active',
                'requirements': {'login_streak': 7},
                'points_reward': 300,
                'max_participants': 200,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=14),
                'is_active': True
            },
            {
                'title': 'Especialista Semanal',
                'description': 'Complete 3 desafios diferentes em uma semana',
                'challenge_type': 'social',
                'status': 'upcoming',
                'requirements': {'challenges_completed': 3, 'time_limit': 7},
                'points_reward': 500,
                'max_participants': 100,
                'start_date': timezone.now() + timedelta(days=2),
                'end_date': timezone.now() + timedelta(days=9),
                'is_active': True
            }
        ]

        for challenge_data in challenges_data:
            # Get or create badge for challenge
            badge = None
            if challenge_data['challenge_type'] == 'prediction':
                badge = Badge.objects.filter(name='Primeira Predição').first()
            elif challenge_data['challenge_type'] == 'streak':
                badge = Badge.objects.filter(name='Sequência de Fogo').first()
            
            challenge, created = Challenge.objects.get_or_create(
                title=challenge_data['title'],
                defaults={**challenge_data, 'badge_reward': badge}
            )
            if created:
                self.stdout.write(f'Created challenge: {challenge.title}')

    def create_fantasy_leagues(self):
        """Create sample fantasy leagues"""
        # Get first competition and season
        competition = Competition.objects.first()
        season = Season.objects.first()
        
        if not competition or not season:
            self.stdout.write(
                self.style.WARNING('No competitions or seasons found. Skipping fantasy leagues.')
            )
            return

        # Get first user as creator
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.WARNING('No users found. Skipping fantasy leagues.')
            )
            return

        fantasy_leagues_data = [
            {
                'id': str(uuid.uuid4())[:8],
                'name': 'Liga dos Amigos',
                'description': 'Liga privada para amigos',
                'league_type': 'private',
                'max_participants': 10,
                'entry_fee_points': 100,
                'prize_pool': 800,
                'join_code': 'AMIGOS01',
                'competition': competition,
                'created_by': user,
                'season': season,
                'starts_at': timezone.now(),
                'ends_at': timezone.now() + timedelta(days=90)
            },
            {
                'id': str(uuid.uuid4())[:8],
                'name': 'Liga Pública Geral',
                'description': 'Liga aberta para todos os usuários',
                'league_type': 'public',
                'max_participants': 100,
                'entry_fee_points': 50,
                'prize_pool': 4000,
                'join_code': 'PUBLIC01',
                'competition': competition,
                'created_by': user,
                'season': season,
                'starts_at': timezone.now(),
                'ends_at': timezone.now() + timedelta(days=120)
            }
        ]

        for league_data in fantasy_leagues_data:
            league, created = FantasyLeague.objects.get_or_create(
                id=league_data['id'],
                defaults=league_data
            )
            if created:
                self.stdout.write(f'Created fantasy league: {league.name}')

    def create_user_profiles(self):
        """Create user profiles for existing users"""
        users = User.objects.all()
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'total_points': 1000,  # Starting points
                    'level': 1,
                    'experience_points': 500,
                    'prediction_streak': 0,
                    'login_streak': 1,
                    'last_login_date': timezone.now().date()
                }
            )
            if created:
                self.stdout.write(f'Created profile for user: {user.username}')
