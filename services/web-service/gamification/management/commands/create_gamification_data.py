"""
Command to create sample gamification data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gamification.models import (
    UserProfile, Badge, UserBadge, FantasyLeague, FantasyTeam,
    PredictionGame, Prediction, Challenge, UserChallenge,
    PointTransaction, Leaderboard, LeaderboardEntry
)
from core.models import Team, Competition, Match, Player
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Create sample gamification data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users', 
            type=int, 
            default=5, 
            help='Number of test users to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating gamification test data...')
        
        # Create test users
        users_created = 0
        for i in range(options['users']):
            username = f'test_user_{i+1}'
            email = f'test{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test{i+1}',
                    'last_name': 'User'
                }
            )
            
            if created:
                users_created += 1
                # Create user profile
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'total_points': random.randint(100, 1000),
                        'level': random.randint(1, 10),
                        'experience_points': random.randint(0, 500),
                        'prediction_streak': random.randint(0, 10),
                        'login_streak': random.randint(0, 30)
                    }
                )
        
        self.stdout.write(f'Created {users_created} test users')
        
        # Create additional badges if needed
        badge_data = [
            ('PREDICTION_MASTER', 'PREDICTION', 'Make 10 correct predictions'),
            ('FANTASY_EXPERT', 'FANTASY', 'Win a fantasy league'),
            ('CHALLENGE_CHAMPION', 'CHALLENGE', 'Complete 5 challenges'),
            ('LOYAL_FAN', 'ENGAGEMENT', 'Login for 30 consecutive days'),
            ('NEWCOMER', 'MILESTONE', 'Welcome to Mark Foot!'),
        ]
        
        badges_created = 0
        for name, badge_type, description in badge_data:
            badge, created = Badge.objects.get_or_create(
                name=name,
                badge_type=badge_type,
                defaults={
                    'description': description,
                    'rarity': random.choice(['COMMON', 'RARE', 'EPIC', 'LEGENDARY']),
                    'points_reward': random.randint(10, 100),
                    'required_predictions': random.randint(5, 20) if badge_type == 'PREDICTION' else None,
                    'required_streak': random.randint(3, 10) if badge_type == 'ENGAGEMENT' else None,
                    'required_fantasy_points': random.randint(100, 500) if badge_type == 'FANTASY' else None,
                    'is_active': True
                }
            )
            if created:
                badges_created += 1
        
        self.stdout.write(f'Created {badges_created} additional badges')
        
        # Award badges to users
        users = User.objects.filter(username__startswith='test_user_')
        badges = Badge.objects.all()[:5]  # Get first 5 badges
        
        badges_awarded = 0
        for user in users:
            # Award random badges
            for badge in random.sample(list(badges), min(3, len(badges))):
                user_badge, created = UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge,
                    defaults={
                        'earned_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                        'is_showcased': random.choice([True, False])
                    }
                )
                if created:
                    badges_awarded += 1
        
        self.stdout.write(f'Awarded {badges_awarded} badges to users')
        
        # Create fantasy leagues
        leagues_created = 0
        try:
            # Get an existing competition
            competition = Competition.objects.first()
            if not competition:
                self.stdout.write('No competitions found, skipping fantasy leagues')
                leagues_created = 0
            else:
                for i in range(3):
                    league, created = FantasyLeague.objects.get_or_create(
                        name=f'Test League {i+1}',
                        defaults={
                            'description': f'Test fantasy league {i+1}',
                            'league_type': random.choice(['PUBLIC', 'PRIVATE']),
                            'max_participants': random.randint(10, 20),
                            'entry_fee_points': random.randint(0, 100),
                            'prize_pool': random.randint(100, 1000),
                            'starts_at': timezone.now(),
                            'ends_at': timezone.now() + timedelta(days=90),
                            'is_active': True,
                            'join_code': f'T{i+1}',
                            'competition': competition
                        }
                    )
                    if created:
                        leagues_created += 1
        except Exception as e:
            self.stdout.write(f'Could not create fantasy leagues: {e}')
            leagues_created = 0
        
        self.stdout.write(f'Created {leagues_created} fantasy leagues')
        
        # Create fantasy teams for users
        teams_created = 0
        leagues = FantasyLeague.objects.all()[:2]  # Use first 2 leagues
        
        for user in users[:3]:  # First 3 test users
            for league in leagues:
                team, created = FantasyTeam.objects.get_or_create(
                    name=f'{user.username} Team',
                    owner=user,
                    league=league,
                    defaults={
                        'formation': '4-4-2',
                        'remaining_budget': 100.0,
                        'total_points': random.randint(50, 200)
                    }
                )
                if created:
                    teams_created += 1
        
        self.stdout.write(f'Created {teams_created} fantasy teams')
        
        # Create prediction games
        games_created = 0
        try:
            # Get some matches for prediction games
            matches = Match.objects.all()[:5]
            
            for i, match in enumerate(matches):
                game, created = PredictionGame.objects.get_or_create(
                    title=f'Predict {match.home_team.name} vs {match.away_team.name}',
                    defaults={
                        'description': f'Predict the outcome of this match',
                        'match': match,
                        'game_type': 'match_result',
                        'start_date': timezone.now().date(),
                        'end_date': (timezone.now() + timedelta(days=7)).date(),
                        'points_reward': random.randint(10, 50),
                        'is_active': True
                    }
                )
                if created:
                    games_created += 1
        except Exception as e:
            self.stdout.write(f'Could not create prediction games: {e}')
        
        self.stdout.write(f'Created {games_created} prediction games')
        
        # Create challenges
        challenges_created = 0
        challenge_data = [
            ('Weekly Predictor', 'Make 5 predictions this week'),
            ('Fantasy Manager', 'Update your fantasy team'),
            ('Social Butterfly', 'Share 3 predictions'),
        ]
        
        for title, description in challenge_data:
            challenge, created = Challenge.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'challenge_type': random.choice(['DAILY', 'WEEKLY', 'MONTHLY']),
                    'status': 'ACTIVE',
                    'requirements': {'target_count': random.randint(3, 10)},
                    'points_reward': random.randint(20, 100),
                    'max_participants': random.randint(50, 200),
                    'current_participants': 0,
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=7)).date()
                }
            )
            if created:
                challenges_created += 1
        
        self.stdout.write(f'Created {challenges_created} challenges')
        
        # Join users to challenges
        participations_created = 0
        challenges = Challenge.objects.all()
        
        for user in users:
            for challenge in random.sample(list(challenges), min(2, len(challenges))):
                participation, created = UserChallenge.objects.get_or_create(
                    user=user,
                    challenge=challenge,
                    defaults={
                        'status': random.choice(['active', 'completed']),
                        'completion_percentage': random.randint(0, 100),
                        'joined_at': timezone.now() - timedelta(days=random.randint(1, 5))
                    }
                )
                if created:
                    participations_created += 1
        
        self.stdout.write(f'Created {participations_created} challenge participations')
        
        # Create leaderboards
        leaderboards_created = 0
        leaderboard_data = [
            ('weekly_predictions', 'Weekly Predictions', 'WEEKLY'),
            ('monthly_fantasy', 'Monthly Fantasy', 'MONTHLY'),
            ('overall_points', 'Overall Points', 'ALL_TIME'),
        ]
        
        for name, description, lb_type in leaderboard_data:
            leaderboard, created = Leaderboard.objects.get_or_create(
                name=name,
                defaults={
                    'leaderboard_type': lb_type,
                    'description': description,
                    'is_active': True,
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + timedelta(days=30)).date()
                }
            )
            if created:
                leaderboards_created += 1
        
        self.stdout.write(f'Created {leaderboards_created} leaderboards')
        
        # Create leaderboard entries
        entries_created = 0
        leaderboards = Leaderboard.objects.all()
        
        for leaderboard in leaderboards:
            rank = 1
            for user in users:
                entry, created = LeaderboardEntry.objects.get_or_create(
                    user=user,
                    leaderboard=leaderboard,
                    defaults={
                        'rank': rank,
                        'score': random.randint(100, 1000),
                        'additional_data': {'total_predictions': random.randint(5, 50)}
                    }
                )
                if created:
                    entries_created += 1
                    rank += 1
        
        self.stdout.write(f'Created {entries_created} leaderboard entries')
        
        # Create point transactions
        transactions_created = 0
        transaction_types = ['prediction_correct', 'challenge_completed', 'badge_earned', 'fantasy_win']
        
        for user in users:
            for _ in range(random.randint(5, 15)):
                transaction = PointTransaction.objects.create(
                    user=user,
                    transaction_type=random.choice(transaction_types),
                    points=random.randint(5, 100),
                    description=f'Points earned from {random.choice(transaction_types).replace("_", " ")}',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                transactions_created += 1
        
        self.stdout.write(f'Created {transactions_created} point transactions')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created gamification test data:\n'
                f'- {users_created} test users\n'
                f'- {badges_created} additional badges\n'
                f'- {badges_awarded} badge awards\n'
                f'- {leagues_created} fantasy leagues\n'
                f'- {teams_created} fantasy teams\n'
                f'- {games_created} prediction games\n'
                f'- {challenges_created} challenges\n'
                f'- {participations_created} challenge participations\n'
                f'- {leaderboards_created} leaderboards\n'
                f'- {entries_created} leaderboard entries\n'
                f'- {transactions_created} point transactions'
            )
        )
