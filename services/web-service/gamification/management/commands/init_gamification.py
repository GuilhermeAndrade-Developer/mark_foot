"""
Management command to initialize the gamification system with default data.
Creates default badges, challenges, and sample leagues.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from gamification.models import Badge, WeeklyChallenge, FantasyLeague
from core.models import Competition


class Command(BaseCommand):
    help = 'Initialize gamification system with default data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all gamification data (careful!)',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🔄 Resetting gamification data...')
            Badge.objects.all().delete()
            WeeklyChallenge.objects.all().delete()
            FantasyLeague.objects.filter(creator__isnull=True).delete()
        
        self.stdout.write('🎮 Initializing gamification system...')
        
        # Create default badges
        self.create_default_badges()
        
        # Create sample weekly challenges
        self.create_sample_challenges()
        
        # Create sample fantasy leagues
        self.create_sample_leagues()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Gamification system initialized successfully!')
        )
    
    def create_default_badges(self):
        """Create default achievement badges"""
        self.stdout.write('🏆 Creating default badges...')
        
        badges_data = [
            # Prediction badges
            {
                'name': 'Primeiro Palpite',
                'description': 'Fez sua primeira predição',
                'icon': '🎯',
                'rarity': 'common',
                'category': 'prediction',
                'points_required': 0,
                'points_reward': 10,
                'conditions': {'min_predictions': 1}
            },
            {
                'name': 'Vidente',
                'description': 'Acertou 10 predições consecutivas',
                'icon': '🔮',
                'rarity': 'rare',
                'category': 'prediction',
                'points_required': 100,
                'points_reward': 100,
                'conditions': {'min_predictions': 10, 'min_accuracy': 80}
            },
            {
                'name': 'Oráculo',
                'description': 'Mantém 90% de acerto em 50+ predições',
                'icon': '👁️',
                'rarity': 'legendary',
                'category': 'prediction',
                'points_required': 1000,
                'points_reward': 500,
                'conditions': {'min_predictions': 50, 'min_accuracy': 90}
            },
            
            # Fantasy badges
            {
                'name': 'Primeiro Time',
                'description': 'Criou seu primeiro time fantasy',
                'icon': '⚽',
                'rarity': 'common',
                'category': 'fantasy',
                'points_required': 0,
                'points_reward': 25,
                'conditions': {'fantasy_leagues': 1}
            },
            {
                'name': 'Técnico Experiente',
                'description': 'Participou de 5 ligas fantasy',
                'icon': '🧠',
                'rarity': 'uncommon',
                'category': 'fantasy',
                'points_required': 200,
                'points_reward': 75,
                'conditions': {'fantasy_leagues': 5}
            },
            {
                'name': 'Lenda Fantasy',
                'description': 'Venceu 3 ligas fantasy',
                'icon': '👑',
                'rarity': 'epic',
                'category': 'fantasy',
                'points_required': 2000,
                'points_reward': 300,
                'conditions': {'fantasy_leagues': 10}
            },
            
            # Social badges
            {
                'name': 'Sociável',
                'description': 'Comentou em 10 partidas',
                'icon': '💬',
                'rarity': 'common',
                'category': 'social',
                'points_required': 50,
                'points_reward': 30,
                'conditions': {}
            },
            {
                'name': 'Influencer',
                'description': 'Recebeu 100 likes em comentários',
                'icon': '⭐',
                'rarity': 'rare',
                'category': 'social',
                'points_required': 500,
                'points_reward': 150,
                'conditions': {}
            },
            
            # Engagement badges
            {
                'name': 'Fiel Torcedor',
                'description': 'Fez login por 7 dias consecutivos',
                'icon': '🔥',
                'rarity': 'uncommon',
                'category': 'engagement',
                'points_required': 0,
                'points_reward': 50,
                'conditions': {'min_streak': 7}
            },
            {
                'name': 'Maratonista',
                'description': 'Fez login por 30 dias consecutivos',
                'icon': '🏃',
                'rarity': 'rare',
                'category': 'engagement',
                'points_required': 300,
                'points_reward': 200,
                'conditions': {'min_streak': 30}
            },
            {
                'name': 'Dedicado',
                'description': 'Fez login por 100 dias consecutivos',
                'icon': '💎',
                'rarity': 'legendary',
                'category': 'engagement',
                'points_required': 1000,
                'points_reward': 1000,
                'conditions': {'min_streak': 100}
            },
            
            # Achievement badges
            {
                'name': 'Colecionador',
                'description': 'Conquistou 10 badges diferentes',
                'icon': '🎁',
                'rarity': 'epic',
                'category': 'achievement',
                'points_required': 1500,
                'points_reward': 400,
                'conditions': {}
            },
            {
                'name': 'Mestre',
                'description': 'Chegou ao nível 10',
                'icon': '🎖️',
                'rarity': 'epic',
                'category': 'achievement',
                'points_required': 5000,
                'points_reward': 500,
                'conditions': {}
            },
            
            # Special badges
            {
                'name': 'Beta Tester',
                'description': 'Participou do período beta',
                'icon': '🧪',
                'rarity': 'legendary',
                'category': 'special',
                'points_required': 0,
                'points_reward': 1000,
                'conditions': {}
            },
        ]
        
        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Created badge: {badge.name}')
        
        self.stdout.write(f'📊 Created {created_count} badges')
    
    def create_sample_challenges(self):
        """Create sample weekly challenges"""
        self.stdout.write('🎯 Creating sample challenges...')
        
        now = timezone.now()
        
        challenges_data = [
            {
                'title': 'Acerte 5 Predições',
                'description': 'Faça 5 predições corretas esta semana',
                'type': 'prediction',
                'status': 'active',
                'start_date': now,
                'end_date': now + timedelta(days=7),
                'requirements': {'correct_predictions': 5},
                'points_reward': 100,
                'max_participants': 1000
            },
            {
                'title': 'Crie um Time Fantasy',
                'description': 'Monte seu primeiro time fantasy nesta semana',
                'type': 'fantasy',
                'status': 'active',
                'start_date': now,
                'end_date': now + timedelta(days=7),
                'requirements': {'create_fantasy_team': 1},
                'points_reward': 150,
                'max_participants': 500
            },
            {
                'title': 'Especialista em Gols',
                'description': 'Acerte o número exato de gols em 3 partidas',
                'type': 'prediction',
                'status': 'upcoming',
                'start_date': now + timedelta(days=7),
                'end_date': now + timedelta(days=14),
                'requirements': {'exact_score_predictions': 3},
                'points_reward': 200,
                'max_participants': 200
            },
            {
                'title': 'Maratona de Engajamento',
                'description': 'Faça login todos os dias da semana',
                'type': 'social',
                'status': 'upcoming',
                'start_date': now + timedelta(days=3),
                'end_date': now + timedelta(days=10),
                'requirements': {'daily_logins': 7},
                'points_reward': 75,
                'max_participants': 1000
            }
        ]
        
        created_count = 0
        for challenge_data in challenges_data:
            challenge, created = WeeklyChallenge.objects.get_or_create(
                title=challenge_data['title'],
                defaults=challenge_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Created challenge: {challenge.title}')
        
        self.stdout.write(f'📊 Created {created_count} challenges')
    
    def create_sample_leagues(self):
        """Create sample fantasy leagues"""
        self.stdout.write('⚽ Creating sample fantasy leagues...')
        
        # Get a competition to use
        competition = Competition.objects.first()
        if not competition:
            self.stdout.write('⚠️  No competitions found, skipping league creation')
            return
        
        now = timezone.now()
        
        leagues_data = [
            {
                'name': 'Liga dos Campeões Fantasy',
                'description': 'Liga premium para os melhores jogadores',
                'type': 'premium',
                'status': 'active',
                'max_participants': 20,
                'entry_fee_points': 100,
                'start_date': now + timedelta(days=1),
                'end_date': now + timedelta(days=90),
                'registration_deadline': now + timedelta(hours=48),
                'total_prize_points': 1500,
                'prize_distribution': {
                    '1st': 800,
                    '2nd': 400,
                    '3rd': 200,
                    'participation': 100
                },
                'scoring_rules': {
                    'goal': 10,
                    'assist': 5,
                    'clean_sheet': 3,
                    'yellow_card': -1,
                    'red_card': -3
                },
                'competition': competition
            },
            {
                'name': 'Liga Iniciante',
                'description': 'Perfeita para quem está começando no fantasy',
                'type': 'public',
                'status': 'active',
                'max_participants': 50,
                'entry_fee_points': 0,
                'start_date': now + timedelta(days=2),
                'end_date': now + timedelta(days=60),
                'registration_deadline': now + timedelta(days=1),
                'total_prize_points': 500,
                'prize_distribution': {
                    '1st': 200,
                    '2nd': 100,
                    '3rd': 50,
                    'top_10': 150
                },
                'scoring_rules': {
                    'goal': 8,
                    'assist': 4,
                    'clean_sheet': 2,
                    'yellow_card': -1,
                    'red_card': -2
                },
                'competition': competition
            },
            {
                'name': 'Liga VIP Brasileirão',
                'description': 'Liga exclusiva focada no Campeonato Brasileiro',
                'type': 'private',
                'status': 'draft',
                'max_participants': 12,
                'entry_fee_points': 200,
                'start_date': now + timedelta(days=7),
                'end_date': now + timedelta(days=120),
                'registration_deadline': now + timedelta(days=5),
                'total_prize_points': 2000,
                'prize_distribution': {
                    '1st': 1000,
                    '2nd': 600,
                    '3rd': 400
                },
                'scoring_rules': {
                    'goal': 12,
                    'assist': 6,
                    'clean_sheet': 4,
                    'penalty_saved': 5,
                    'yellow_card': -1,
                    'red_card': -4
                },
                'competition': competition
            }
        ]
        
        created_count = 0
        for league_data in leagues_data:
            league, created = FantasyLeague.objects.get_or_create(
                name=league_data['name'],
                defaults=league_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Created league: {league.name}')
        
        self.stdout.write(f'📊 Created {created_count} fantasy leagues')
