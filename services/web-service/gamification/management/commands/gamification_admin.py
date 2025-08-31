"""
Management command for gamification administration.
Allows admins to manage points, badges, and other gamification features.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum
from gamification.models import (
    UserProfile, Badge, UserBadge, PointsTransaction,
    Prediction, FantasyTeam, ChallengeParticipation
)


class Command(BaseCommand):
    help = 'Manage gamification system: points, badges, leaderboards'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['stats', 'award_badge', 'add_points', 'leaderboard', 'reset_user'],
            help='Action to perform'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username for user-specific actions'
        )
        parser.add_argument(
            '--badge',
            type=str,
            help='Badge name to award'
        )
        parser.add_argument(
            '--points',
            type=int,
            help='Points to add/remove'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='Manual adjustment',
            help='Reason for points transaction'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit for leaderboard results'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'stats':
            self.show_stats()
        elif action == 'award_badge':
            self.award_badge(options)
        elif action == 'add_points':
            self.add_points(options)
        elif action == 'leaderboard':
            self.show_leaderboard(options['limit'])
        elif action == 'reset_user':
            self.reset_user(options)
    
    def show_stats(self):
        """Show overall gamification statistics"""
        self.stdout.write('📊 GAMIFICATION STATISTICS')
        self.stdout.write('=' * 50)
        
        # User stats
        total_users = User.objects.count()
        active_profiles = UserProfile.objects.filter(total_points__gt=0).count()
        
        self.stdout.write(f'👥 Total Users: {total_users}')
        self.stdout.write(f'🎮 Active Gamification Profiles: {active_profiles}')
        
        # Points stats
        total_points = UserProfile.objects.aggregate(
            total=Sum('total_points')
        )['total'] or 0
        avg_points = UserProfile.objects.aggregate(
            avg=Avg('total_points')
        )['avg'] or 0
        
        self.stdout.write(f'💰 Total Points in System: {total_points:,}')
        self.stdout.write(f'📈 Average Points per User: {avg_points:.1f}')
        
        # Level distribution
        level_distribution = UserProfile.objects.values('level').annotate(
            count=Count('id')
        ).order_by('level')
        
        self.stdout.write('\\n🏆 Level Distribution:')
        for level_data in level_distribution:
            level = level_data['level']
            count = level_data['count']
            percentage = (count / total_users) * 100 if total_users > 0 else 0
            self.stdout.write(f'  Level {level}: {count} users ({percentage:.1f}%)')
        
        # Badge stats
        total_badges = Badge.objects.count()
        active_badges = Badge.objects.filter(is_active=True).count()
        earned_badges = UserBadge.objects.count()
        
        self.stdout.write(f'\\n🏅 Badge Statistics:')
        self.stdout.write(f'  Total Badges: {total_badges}')
        self.stdout.write(f'  Active Badges: {active_badges}')
        self.stdout.write(f'  Times Earned: {earned_badges}')
        
        # Most earned badges
        popular_badges = Badge.objects.annotate(
            earned_count=Count('earned_by')
        ).order_by('-earned_count')[:5]
        
        self.stdout.write('\\n🔥 Most Popular Badges:')
        for badge in popular_badges:
            self.stdout.write(f'  {badge.name}: {badge.earned_count} times')
        
        # Prediction stats
        total_predictions = Prediction.objects.count()
        correct_predictions = Prediction.objects.filter(status='correct').count()
        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        self.stdout.write(f'\\n🎯 Prediction Statistics:')
        self.stdout.write(f'  Total Predictions: {total_predictions}')
        self.stdout.write(f'  Correct Predictions: {correct_predictions}')
        self.stdout.write(f'  Overall Accuracy: {accuracy:.1f}%')
        
        # Fantasy stats
        total_teams = FantasyTeam.objects.count()
        active_leagues = FantasyTeam.objects.values('league').distinct().count()
        
        self.stdout.write(f'\\n⚽ Fantasy Statistics:')
        self.stdout.write(f'  Total Fantasy Teams: {total_teams}')
        self.stdout.write(f'  Active Leagues: {active_leagues}')
        
        # Challenge stats
        total_participations = ChallengeParticipation.objects.count()
        completed_challenges = ChallengeParticipation.objects.filter(
            status='completed'
        ).count()
        
        self.stdout.write(f'\\n🎯 Challenge Statistics:')
        self.stdout.write(f'  Total Participations: {total_participations}')
        self.stdout.write(f'  Completed Challenges: {completed_challenges}')
    
    def award_badge(self, options):
        """Award a badge to a user"""
        username = options.get('user')
        badge_name = options.get('badge')
        
        if not username or not badge_name:
            self.stdout.write(
                self.style.ERROR('❌ Both --user and --badge are required')
            )
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User "{username}" not found')
            )
            return
        
        try:
            badge = Badge.objects.get(name=badge_name)
        except Badge.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Badge "{badge_name}" not found')
            )
            return
        
        # Check if user already has the badge
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  User {username} already has badge "{badge_name}"')
            )
            return
        
        # Award the badge
        user_badge = UserBadge.objects.create(user=user, badge=badge)
        
        # Award points
        profile = user.gamification_profile
        profile.total_points += badge.points_reward
        profile.save()
        
        # Create transaction
        PointsTransaction.objects.create(
            user=user,
            type='bonus',
            amount=badge.points_reward,
            source_type='Badge',
            source_id=badge.id,
            description=f'Manual badge award: {badge.name}',
            balance_before=profile.total_points - badge.points_reward,
            balance_after=profile.total_points
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Awarded badge "{badge.name}" to {username} (+{badge.points_reward} points)'
            )
        )
    
    def add_points(self, options):
        """Add or remove points from a user"""
        username = options.get('user')
        points = options.get('points')
        reason = options.get('reason')
        
        if not username or points is None:
            self.stdout.write(
                self.style.ERROR('❌ Both --user and --points are required')
            )
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User "{username}" not found')
            )
            return
        
        profile = user.gamification_profile
        old_balance = profile.total_points
        
        # Prevent negative balance
        if profile.total_points + points < 0:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Cannot reduce points below 0. User has {profile.total_points} points'
                )
            )
            return
        
        # Update points
        profile.total_points += points
        profile.save()
        
        # Create transaction
        transaction_type = 'earned' if points > 0 else 'spent'
        PointsTransaction.objects.create(
            user=user,
            type=transaction_type,
            amount=points,
            source_type='Manual',
            source_id=0,
            description=reason,
            balance_before=old_balance,
            balance_after=profile.total_points
        )
        
        action = 'Added' if points > 0 else 'Removed'
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {action} {abs(points)} points to {username}. '
                f'New balance: {profile.total_points}'
            )
        )
    
    def show_leaderboard(self, limit):
        """Show current leaderboard"""
        self.stdout.write(f'🏆 TOP {limit} LEADERBOARD')
        self.stdout.write('=' * 50)
        
        top_users = UserProfile.objects.select_related('user').annotate(
            badges_count=Count('user__earned_badges')
        ).order_by('-total_points')[:limit]
        
        for i, profile in enumerate(top_users, 1):
            self.stdout.write(
                f'{i:2d}. {profile.user.username:20s} | '
                f'Level {profile.level:2d} | '
                f'{profile.total_points:6,d} pts | '
                f'{profile.badges_count:2d} badges | '
                f'{profile.accuracy_percentage:5.1f}% accuracy'
            )
    
    def reset_user(self, options):
        """Reset a user's gamification data"""
        username = options.get('user')
        
        if not username:
            self.stdout.write(
                self.style.ERROR('❌ --user is required')
            )
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ User "{username}" not found')
            )
            return
        
        # Confirm reset
        confirm = input(f'⚠️  Are you sure you want to reset all gamification data for {username}? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('❌ Reset cancelled')
            return
        
        # Reset profile
        profile = user.gamification_profile
        profile.total_points = 0
        profile.level = 1
        profile.experience_points = 0
        profile.streak_days = 0
        profile.total_predictions = 0
        profile.correct_predictions = 0
        profile.prediction_accuracy = 0
        profile.save()
        
        # Remove badges
        UserBadge.objects.filter(user=user).delete()
        
        # Remove transactions
        PointsTransaction.objects.filter(user=user).delete()
        
        # Remove predictions
        Prediction.objects.filter(user=user).delete()
        
        # Remove fantasy teams
        FantasyTeam.objects.filter(user=user).delete()
        
        # Remove challenge participations
        ChallengeParticipation.objects.filter(user=user).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Reset all gamification data for {username}')
        )
