"""
Global pytest configuration and fixtures for Mark Foot project.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import pytest

# Add the Django project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'web-service'))

def pytest_configure():
    """Configure Django settings for pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }


@pytest.fixture
def api_client():
    """Create API client for testing"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Create authenticated API client"""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def test_competition(db):
    """Create a test competition"""
    from core.models import Competition, Area
    area, _ = Area.objects.get_or_create(
        name='England',
        code='ENG',
        flag='https://example.com/flag.png'
    )
    return Competition.objects.create(
        name='Test League',
        code='TL',
        area=area,
        plan='TIER_ONE'
    )


@pytest.fixture
def test_team(db, test_competition):
    """Create a test team"""
    from core.models import Team
    return Team.objects.create(
        name='Test Team',
        short_name='TT',
        tla='TTM',
        area=test_competition.area,
        address='Test Address'
    )


@pytest.fixture
def test_match(db, test_competition, test_team):
    """Create a test match"""
    from core.models import Match, Season
    from datetime import datetime, timezone
    
    # Create another team for away team
    away_team, _ = Team.objects.get_or_create(
        name='Away Team',
        short_name='AT',
        tla='ATM',
        area=test_competition.area,
        address='Away Address'
    )
    
    season, _ = Season.objects.get_or_create(
        competition=test_competition,
        start_date='2024-08-01',
        end_date='2025-07-31',
        current_matchday=1
    )
    
    return Match.objects.create(
        competition=test_competition,
        season=season,
        home_team=test_team,
        away_team=away_team,
        utc_date=datetime.now(timezone.utc),
        status='SCHEDULED',
        matchday=1,
        stage='REGULAR_SEASON'
    )
