"""
Tests for gamification system.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from .models import (
    UserProfile, Badge, UserBadge, FantasyLeague, FantasyTeam,
    Prediction, WeeklyChallenge, PointsTransaction
)
from core.models import Competition, Team, Match, Player


class UserProfileTestCase(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_created_automatically(self):
        """Test that profile is created when user is created"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.total_points, 0)
        self.assertEqual(profile.level, 1)
    
    def test_accuracy_percentage_calculation(self):
        """Test prediction accuracy calculation"""
        profile = self.user.gamification_profile
        profile.total_predictions = 10
        profile.correct_predictions = 8
        
        self.assertEqual(profile.accuracy_percentage, 80.0)
    
    def test_accuracy_percentage_zero_predictions(self):
        """Test accuracy when no predictions made"""
        profile = self.user.gamification_profile
        self.assertEqual(profile.accuracy_percentage, 0)


class BadgeTestCase(TestCase):
    """Test cases for Badge system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.badge = Badge.objects.create(
            name='Test Badge',
            description='A test badge',
            icon='🏆',
            rarity='common',
            category='test',
            points_reward=50
        )
    
    def test_badge_creation(self):
        """Test badge creation"""
        self.assertEqual(self.badge.name, 'Test Badge')
        self.assertEqual(self.badge.points_reward, 50)
    
    def test_user_badge_award(self):
        """Test awarding badge to user"""
        user_badge = UserBadge.objects.create(
            user=self.user,
            badge=self.badge
        )
        
        self.assertEqual(user_badge.user, self.user)
        self.assertEqual(user_badge.badge, self.badge)
        self.assertTrue(user_badge.earned_at)


class FantasyLeagueTestCase(TestCase):
    """Test cases for Fantasy League system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.competition = Competition.objects.create(
            name='Test Competition',
            code='TC',
            area_name='Test Area'
        )
        self.league = FantasyLeague.objects.create(
            name='Test League',
            creator=self.user,
            max_participants=10,
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            registration_deadline=timezone.now() + timedelta(hours=12),
            competition=self.competition
        )
    
    def test_league_creation(self):
        """Test fantasy league creation"""
        self.assertEqual(self.league.name, 'Test League')
        self.assertEqual(self.league.creator, self.user)
        self.assertEqual(self.league.participants_count, 0)
    
    def test_league_joinable(self):
        """Test if league is joinable"""
        # Should be joinable initially
        self.assertTrue(self.league.is_joinable)
        
        # Change status to active - should not be joinable
        self.league.status = 'active'
        self.league.save()
        self.assertFalse(self.league.is_joinable)


class PredictionTestCase(TestCase):
    """Test cases for Prediction system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create teams
        self.team1 = Team.objects.create(
            name='Team A',
            short_name='TA',
            tla='TAA'
        )
        self.team2 = Team.objects.create(
            name='Team B',
            short_name='TB',
            tla='TBB'
        )
        
        # Create match
        self.match = Match.objects.create(
            home_team=self.team1,
            away_team=self.team2,
            utc_date=timezone.now() + timedelta(days=1),
            status='SCHEDULED'
        )
    
    def test_prediction_creation(self):
        """Test prediction creation"""
        prediction = Prediction.objects.create(
            user=self.user,
            match=self.match,
            predicted_result='1',
            confidence=8,
            points_bet=50
        )
        
        self.assertEqual(prediction.user, self.user)
        self.assertEqual(prediction.match, self.match)
        self.assertEqual(prediction.predicted_result, '1')
        self.assertEqual(prediction.status, 'pending')
    
    def test_points_calculation_correct_result(self):
        """Test points calculation for correct prediction"""
        prediction = Prediction.objects.create(
            user=self.user,
            match=self.match,
            predicted_result='1',
            predicted_home_score=2,
            predicted_away_score=1,
            confidence=8,
            points_bet=50
        )
        
        # Simulate match finish
        self.match.status = 'FINISHED'
        self.match.score_home = 2
        self.match.score_away = 1
        self.match.save()
        
        points = prediction.calculate_points()
        
        # Should get 2x for correct result + 3x bonus for exact score
        # (50 * 2 + 50 * 3) * 0.8 (confidence) = 400
        expected_points = int((50 * 2 + 50 * 3) * (8 / 10))
        self.assertEqual(points, expected_points)


class PointsTransactionTestCase(TestCase):
    """Test cases for Points Transaction system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_transaction_creation(self):
        """Test points transaction creation"""
        profile = self.user.gamification_profile
        initial_balance = profile.total_points
        
        transaction = PointsTransaction.objects.create(
            user=self.user,
            type='earned',
            amount=100,
            source_type='Test',
            source_id=1,
            description='Test transaction',
            balance_before=initial_balance,
            balance_after=initial_balance + 100
        )
        
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.type, 'earned')


class GamificationAPITestCase(APITestCase):
    """Test cases for Gamification API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        """Test getting user profile via API"""
        url = '/api/gamification/profiles/me/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['total_points'], 0)
        self.assertEqual(response.data['level'], 1)
    
    def test_get_badges(self):
        """Test getting badges via API"""
        # Create a test badge
        Badge.objects.create(
            name='Test Badge',
            description='Test description',
            icon='🏆',
            rarity='common',
            category='test',
            points_reward=50
        )
        
        url = '/api/gamification/badges/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Badge')
    
    def test_create_fantasy_league(self):
        """Test creating fantasy league via API"""
        # Create competition first
        competition = Competition.objects.create(
            name='Test Competition',
            code='TC',
            area_name='Test Area'
        )
        
        url = '/api/gamification/fantasy-leagues/'
        data = {
            'name': 'Test League',
            'description': 'A test league',
            'type': 'public',
            'max_participants': 20,
            'start_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'registration_deadline': (timezone.now() + timedelta(hours=12)).isoformat(),
            'competition': competition.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test League')
        self.assertEqual(response.data['creator_username'], 'testuser')
    
    def test_points_transaction_history(self):
        """Test getting points transaction history"""
        # Create a transaction
        PointsTransaction.objects.create(
            user=self.user,
            type='earned',
            amount=100,
            source_type='Test',
            source_id=1,
            description='Test transaction',
            balance_before=0,
            balance_after=100
        )
        
        url = '/api/gamification/transactions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['amount'], 100)
    
    def test_leaderboard_overall(self):
        """Test overall leaderboard endpoint"""
        url = '/api/gamification/leaderboards/overall/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class ChallengeTestCase(TestCase):
    """Test cases for Weekly Challenge system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.challenge = WeeklyChallenge.objects.create(
            title='Test Challenge',
            description='A test challenge',
            type='prediction',
            status='active',
            start_date=timezone.now() - timedelta(hours=1),
            end_date=timezone.now() + timedelta(days=6),
            points_reward=100
        )
    
    def test_challenge_is_active(self):
        """Test if challenge is active"""
        self.assertTrue(self.challenge.is_active)
    
    def test_challenge_not_active_future(self):
        """Test challenge not active if in future"""
        future_challenge = WeeklyChallenge.objects.create(
            title='Future Challenge',
            description='A future challenge',
            type='prediction',
            status='active',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=7),
            points_reward=100
        )
        
        self.assertFalse(future_challenge.is_active)
    
    def test_challenge_not_active_past(self):
        """Test challenge not active if ended"""
        past_challenge = WeeklyChallenge.objects.create(
            title='Past Challenge',
            description='A past challenge',
            type='prediction',
            status='active',
            start_date=timezone.now() - timedelta(days=7),
            end_date=timezone.now() - timedelta(days=1),
            points_reward=100
        )
        
        self.assertFalse(past_challenge.is_active)
