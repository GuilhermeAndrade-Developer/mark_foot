"""
Tests for chat application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import ChatRoom, ChatMessage, ChatUserSession, ChatModeration
from core.models import Match, Team, Competition, Area


class ChatRoomModelTest(TestCase):
    """Test cases for ChatRoom model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test competition, teams, and match
        self.area = Area.objects.create(
            id=1,
            name='Test Area',
            code='TEST'
        )
        
        self.competition = Competition.objects.create(
            id=1,
            name='Test Competition',
            code='TC',
            area=self.area
        )
        
        self.team1 = Team.objects.create(
            id=1,
            name='Team 1',
            short_name='T1',
            tla='T1'
        )
        
        self.team2 = Team.objects.create(
            id=2,
            name='Team 2',
            short_name='T2',
            tla='T2'
        )
        
        self.match = Match.objects.create(
            id=1,
            home_team=self.team1,
            away_team=self.team2,
            competition=self.competition,
            status='SCHEDULED',
            utc_date=timezone.now() + timedelta(hours=1)
        )
    
    def test_create_general_chat_room(self):
        """Test creating a general chat room."""
        room = ChatRoom.objects.create(
            name='General Chat',
            description='General discussion',
            room_type='general',
            created_by=self.user
        )
        
        self.assertEqual(room.name, 'General Chat')
        self.assertEqual(room.room_type, 'general')
        self.assertEqual(room.status, 'active')
        self.assertTrue(room.can_user_join(self.user))
    
    def test_create_match_chat_room(self):
        """Test creating a match-specific chat room."""
        room = ChatRoom.objects.create(
            name='Match Chat',
            room_type='match',
            match=self.match,
            created_by=self.user
        )
        
        self.assertEqual(room.match, self.match)
        self.assertEqual(room.room_type, 'match')
        self.assertTrue(room.can_user_join(self.user))
    
    def test_room_user_limits(self):
        """Test room user limits."""
        room = ChatRoom.objects.create(
            name='Limited Room',
            max_users=2,
            created_by=self.user
        )
        
        # Create user sessions to fill the room
        user2 = User.objects.create_user(username='user2', password='pass')
        user3 = User.objects.create_user(username='user3', password='pass')
        
        # Add two users
        ChatUserSession.objects.create(room=room, user=self.user, is_active=True)
        ChatUserSession.objects.create(room=room, user=user2, is_active=True)
        
        # Room should be full
        self.assertFalse(room.can_user_join(user3))
    
    def test_inactive_room_join(self):
        """Test that users cannot join inactive rooms."""
        room = ChatRoom.objects.create(
            name='Inactive Room',
            status='inactive',
            created_by=self.user
        )
        
        self.assertFalse(room.can_user_join(self.user))


class ChatMessageModelTest(TestCase):
    """Test cases for ChatMessage model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user
        )
    
    def test_create_message(self):
        """Test creating a chat message."""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.user,
            content='Hello, world!',
            message_type='text'
        )
        
        self.assertEqual(message.content, 'Hello, world!')
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.status, 'active')
        self.assertEqual(message.get_username(), 'testuser')
    
    def test_guest_message(self):
        """Test creating a message from a guest user."""
        message = ChatMessage.objects.create(
            room=self.room,
            guest_name='Guest123',
            content='Hello from guest!',
            message_type='text'
        )
        
        self.assertIsNone(message.user)
        self.assertEqual(message.guest_name, 'Guest123')
        self.assertEqual(message.get_username(), 'Guest123')
    
    def test_message_flagging(self):
        """Test message flagging functionality."""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.user,
            content='Inappropriate content'
        )
        
        # Flag the message
        message.is_flagged = True
        message.flag_count = 1
        message.save()
        
        self.assertTrue(message.is_flagged)
        self.assertEqual(message.flag_count, 1)


class ChatUserSessionModelTest(TestCase):
    """Test cases for ChatUserSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user
        )
    
    def test_create_user_session(self):
        """Test creating a user session."""
        session = ChatUserSession.objects.create(
            room=self.room,
            user=self.user,
            is_active=True
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.room, self.room)
        self.assertTrue(session.is_active)
        self.assertEqual(session.messages_sent, 0)
    
    def test_guest_session(self):
        """Test creating a guest session."""
        session = ChatUserSession.objects.create(
            room=self.room,
            guest_id='guest_123',
            is_active=True
        )
        
        self.assertIsNone(session.user)
        self.assertEqual(session.guest_id, 'guest_123')
        self.assertTrue(session.is_active)


class ChatModerationModelTest(TestCase):
    """Test cases for ChatModeration model."""
    
    def setUp(self):
        """Set up test data."""
        self.moderator = User.objects.create_user(
            username='moderator',
            password='modpass123'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.moderator
        )
        
        self.message = ChatMessage.objects.create(
            room=self.room,
            user=self.user,
            content='Test message'
        )
    
    def test_create_moderation_action(self):
        """Test creating a moderation action."""
        action = ChatModeration.objects.create(
            room=self.room,
            moderator=self.moderator,
            target_user=self.user,
            target_message=self.message,
            action_type='warn',
            reason='Test warning'
        )
        
        self.assertEqual(action.moderator, self.moderator)
        self.assertEqual(action.target_user, self.user)
        self.assertEqual(action.action_type, 'warn')
        self.assertEqual(action.reason, 'Test warning')
        self.assertTrue(action.is_active)
    
    def test_timeout_action(self):
        """Test creating a timeout moderation action."""
        action = ChatModeration.objects.create(
            room=self.room,
            moderator=self.moderator,
            target_user=self.user,
            action_type='timeout',
            reason='Timeout for 60 minutes',
            duration_minutes=60
        )
        
        self.assertEqual(action.action_type, 'timeout')
        self.assertEqual(action.duration_minutes, 60)
        self.assertIsNotNone(action.expires_at)
