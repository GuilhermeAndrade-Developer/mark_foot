"""
Management command for chat operations.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q, F
from datetime import timedelta

from chat.models import (
    ChatRoom, ChatMessage, ChatUserSession, ChatModeration,
    ChatReport, ChatBannedUser
)
from core.models import Match


class Command(BaseCommand):
    """Chat management command."""
    
    help = 'Manage chat rooms and perform maintenance tasks'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            'action',
            choices=[
                'create_match_rooms', 'cleanup_sessions', 'moderate_flagged',
                'stats', 'create_test_data', 'clean_old_messages'
            ],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--match-id',
            type=int,
            help='Match ID for match-specific operations'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days for cleanup operations (default: 7)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limit for bulk operations (default: 100)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without executing'
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        action = options['action']
        
        if action == 'create_match_rooms':
            self.create_match_rooms(options)
        elif action == 'cleanup_sessions':
            self.cleanup_sessions(options)
        elif action == 'moderate_flagged':
            self.moderate_flagged_messages(options)
        elif action == 'stats':
            self.show_stats(options)
        elif action == 'create_test_data':
            self.create_test_data(options)
        elif action == 'clean_old_messages':
            self.clean_old_messages(options)
    
    def create_match_rooms(self, options):
        """Create chat rooms for upcoming matches."""
        self.stdout.write("Creating chat rooms for upcoming matches...")
        
        # Get upcoming matches in the next 7 days
        start_date = timezone.now()
        end_date = start_date + timedelta(days=7)
        
        upcoming_matches = Match.objects.filter(
            utc_date__gte=start_date,
            utc_date__lte=end_date,
            status='SCHEDULED'
        ).exclude(
            chat_room__isnull=False  # Exclude matches that already have chat rooms
        )
        
        if options['match_id']:
            upcoming_matches = upcoming_matches.filter(id=options['match_id'])
        
        created_count = 0
        
        for match in upcoming_matches:
            if options['dry_run']:
                self.stdout.write(
                    f"Would create room for: {match.home_team.name} vs {match.away_team.name}"
                )
                continue
            
            room_name = f"{match.home_team.name} vs {match.away_team.name}"
            
            try:
                room = ChatRoom.objects.create(
                    name=room_name,
                    description=f"Live chat for {room_name} match",
                    room_type='match',
                    match=match,
                    max_users=1000,
                    rate_limit_messages=5,
                    auto_moderation=True,
                    profanity_filter=True,
                    spam_detection=True,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f"Created room: {room.name}")
                )
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create room for {room_name}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} chat rooms")
        )
    
    def cleanup_sessions(self, options):
        """Clean up inactive user sessions."""
        self.stdout.write("Cleaning up inactive user sessions...")
        
        # Mark sessions as inactive if no activity for more than 30 minutes
        cutoff_time = timezone.now() - timedelta(minutes=30)
        
        inactive_sessions = ChatUserSession.objects.filter(
            is_active=True,
            last_activity__lt=cutoff_time
        )
        
        if options['dry_run']:
            count = inactive_sessions.count()
            self.stdout.write(f"Would mark {count} sessions as inactive")
            return
        
        # Update sessions
        updated_count = inactive_sessions.update(
            is_active=False,
            left_at=timezone.now()
        )
        
        # Remove very old sessions (older than specified days)
        old_cutoff = timezone.now() - timedelta(days=options['days'])
        old_sessions = ChatUserSession.objects.filter(
            created_at__lt=old_cutoff,
            is_active=False
        )
        
        deleted_count = old_sessions.count()
        if not options['dry_run']:
            old_sessions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Marked {updated_count} sessions as inactive, "
                f"deleted {deleted_count} old sessions"
            )
        )
    
    def moderate_flagged_messages(self, options):
        """Automatically moderate flagged messages."""
        self.stdout.write("Processing flagged messages...")
        
        # Get messages flagged by multiple users (3 or more)
        flagged_messages = ChatMessage.objects.filter(
            is_flagged=True,
            flag_count__gte=3,
            status='active'
        )[:options['limit']]
        
        if options['dry_run']:
            count = flagged_messages.count()
            self.stdout.write(f"Would hide {count} flagged messages")
            return
        
        # Get or create system moderator
        system_user, created = User.objects.get_or_create(
            username='system_moderator',
            defaults={
                'email': 'system@markfoot.com',
                'is_staff': True,
                'is_active': False  # System user, not for login
            }
        )
        
        hidden_count = 0
        
        for message in flagged_messages:
            # Hide the message
            message.status = 'hidden'
            message.moderated_by = system_user
            message.moderated_at = timezone.now()
            message.moderation_reason = f'Auto-hidden: {message.flag_count} reports'
            message.save()
            
            # Create moderation log
            ChatModeration.objects.create(
                room=message.room,
                moderator=system_user,
                target_user=message.user,
                target_message=message,
                action_type='message_delete',
                reason=f'Auto-moderated: {message.flag_count} user reports'
            )
            
            hidden_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"Auto-hidden {hidden_count} flagged messages")
        )
    
    def show_stats(self, options):
        """Show chat statistics."""
        self.stdout.write("Chat System Statistics")
        self.stdout.write("=" * 50)
        
        # Room stats
        total_rooms = ChatRoom.objects.count()
        active_rooms = ChatRoom.objects.filter(status='active').count()
        
        # Message stats
        total_messages = ChatMessage.objects.count()
        active_messages = ChatMessage.objects.filter(status='active').count()
        flagged_messages = ChatMessage.objects.filter(is_flagged=True).count()
        
        # User stats
        total_sessions = ChatUserSession.objects.count()
        active_sessions = ChatUserSession.objects.filter(is_active=True).count()
        
        # Today's activity
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = ChatMessage.objects.filter(
            created_at__gte=today,
            status='active'
        ).count()
        
        # Moderation stats
        pending_reports = ChatReport.objects.filter(status='pending').count()
        total_bans = ChatBannedUser.objects.filter(is_active=True).count()
        
        self.stdout.write(f"Rooms: {active_rooms}/{total_rooms} active")
        self.stdout.write(f"Messages: {active_messages}/{total_messages} active")
        self.stdout.write(f"Flagged Messages: {flagged_messages}")
        self.stdout.write(f"User Sessions: {active_sessions}/{total_sessions} active")
        self.stdout.write(f"Messages Today: {messages_today}")
        self.stdout.write(f"Pending Reports: {pending_reports}")
        self.stdout.write(f"Active Bans: {total_bans}")
        
        # Top active rooms
        self.stdout.write("\nTop 10 Active Rooms:")
        self.stdout.write("-" * 30)
        
        top_rooms = ChatRoom.objects.filter(status='active').annotate(
            active_users=Count('user_sessions', filter=Q(user_sessions__is_active=True))
        ).order_by('-active_users')[:10]
        
        for room in top_rooms:
            self.stdout.write(f"{room.name}: {room.active_users} users")
    
    def create_test_data(self, options):
        """Create test data for development."""
        if not options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    "This will create test data. Use --dry-run to see what would be created."
                )
            )
            confirm = input("Continue? (y/N): ")
            if confirm.lower() != 'y':
                return
        
        self.stdout.write("Creating test data...")
        
        # Create test users
        test_users = []
        for i in range(5):
            username = f"testuser{i+1}"
            if options['dry_run']:
                self.stdout.write(f"Would create user: {username}")
                continue
                
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@test.com',
                    'first_name': f'Test{i+1}',
                    'last_name': 'User'
                }
            )
            test_users.append(user)
        
        if options['dry_run']:
            self.stdout.write("Would create test chat room and messages")
            return
        
        # Create test room
        test_room, created = ChatRoom.objects.get_or_create(
            name='Test Chat Room',
            defaults={
                'description': 'Test room for development',
                'room_type': 'general',
                'created_by': test_users[0] if test_users else None
            }
        )
        
        # Create test messages
        test_messages = [
            "Hello everyone! 👋",
            "How's everyone doing today?",
            "Great match yesterday! ⚽",
            "Who's excited for the next game?",
            "The team played really well! 🎉"
        ]
        
        for i, content in enumerate(test_messages):
            if i < len(test_users):
                ChatMessage.objects.get_or_create(
                    room=test_room,
                    user=test_users[i],
                    content=content,
                    defaults={'message_type': 'text'}
                )
        
        # Create active sessions
        for user in test_users[:3]:  # Only first 3 users active
            ChatUserSession.objects.get_or_create(
                room=test_room,
                user=user,
                defaults={'is_active': True}
            )
        
        self.stdout.write(
            self.style.SUCCESS("Test data created successfully")
        )
    
    def clean_old_messages(self, options):
        """Clean up old messages."""
        self.stdout.write("Cleaning up old messages...")
        
        cutoff_date = timezone.now() - timedelta(days=options['days'])
        
        old_messages = ChatMessage.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['deleted', 'hidden']
        )
        
        count = old_messages.count()
        
        if options['dry_run']:
            self.stdout.write(f"Would delete {count} old messages")
            return
        
        old_messages.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count} old messages")
        )
