"""
Django signals for gamification system.
Handles automatic point calculations, badge awards, etc.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    UserProfile, Prediction, PredictionGame, PointTransaction, Badge, UserBadge,
    Challenge, UserChallenge
)
from core.models import Match


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Match)
def process_match_predictions(sender, instance, **kwargs):
    """Process all predictions when a match is finished"""
    if instance.status == 'FINISHED' and instance.home_team_score is not None:
        # Find prediction games related to this match
        prediction_games = PredictionGame.objects.filter(
            match=instance,
            status='active'
        )
        
        for game in prediction_games:
            predictions = Prediction.objects.filter(
                game=game,
                is_correct__isnull=True  # Not yet resolved
            )
            
            for prediction in predictions:
                # Simple scoring: exact score = 10 points, correct result = 5 points
                points_earned = 0
                
                actual_home = instance.home_team_score
                actual_away = instance.away_team_score
                
                # Get prediction data from JSON field
                pred_data = prediction.prediction_data or {}
                pred_home = pred_data.get('home_score')
                pred_away = pred_data.get('away_score')
                points_bet = pred_data.get('points_bet', game.entry_fee_points)
                
                if pred_home is not None and pred_away is not None:
                    # Exact score match
                    if actual_home == pred_home and actual_away == pred_away:
                        points_earned = int(points_bet * game.reward_multiplier)
                        prediction.is_correct = True
                    # Correct result (win/draw/loss)
                    elif ((actual_home > actual_away and pred_home > pred_away) or
                          (actual_home < actual_away and pred_home < pred_away) or
                          (actual_home == actual_away and pred_home == pred_away)):
                        points_earned = points_bet  # Return the bet
                        prediction.is_correct = True
                    else:
                        prediction.is_correct = False
                    
                    prediction.points_earned = points_earned
                    prediction.resolved_at = timezone.now()
                    
                    if points_earned > 0:
                        # Update user profile
                        profile = prediction.user.user_profiles.first()
                        if profile:
                            profile.total_points += points_earned
                            profile.save()
                        
                        # Create points transaction
                        PointTransaction.objects.create(
                            user=prediction.user,
                            transaction_type='win',
                            amount=points_earned,
                            description=f'Predição: {instance}',
                            balance_after=profile.total_points if profile else points_earned
                        )
                    
                    prediction.save()
            
            # Update game status
            game.status = 'resolved'
            game.save()


@receiver(post_save, sender=Prediction)
def deduct_bet_points(sender, instance, created, **kwargs):
    """Deduct bet points when prediction is created"""
    if created:
        profile = instance.user.user_profiles.first()
        if profile and profile.total_points >= instance.points_bet:
            profile.total_points -= instance.points_bet
            profile.save()
            
            # Create debit transaction
            PointTransaction.objects.create(
                user=instance.user,
                transaction_type='bet',
                amount=-instance.points_bet,
                description=f'Aposta: {instance.match}',
                balance_after=profile.total_points
            )


@receiver(post_save, sender=PointTransaction)
def check_badge_eligibility(sender, instance, created, **kwargs):
    """Check if user earned new badges after points transaction"""
    if created and instance.amount > 0:
        profile = instance.user.user_profiles.first()
        if not profile:
            return
        
        # Check point-based badges
        badges_to_check = Badge.objects.filter(
            points_required__lte=profile.total_points,
            is_active=True
        ).exclude(
            user_badges__user=instance.user
        )
        
        for badge in badges_to_check:
            UserBadge.objects.get_or_create(
                user=instance.user,
                badge=badge
            )


@receiver(post_save, sender=UserChallenge)
def award_challenge_points(sender, instance, **kwargs):
    """Award points when challenge is completed"""
    if instance.is_completed and instance.points_earned == 0:
        points = instance.challenge.points_reward
        instance.points_earned = points
        instance.save(update_fields=['points_earned'])
        
        # Update user profile
        profile = instance.user.user_profiles.first()
        if profile:
            profile.total_points += points
            profile.save()
            
            # Create points transaction
            PointTransaction.objects.create(
                user=instance.user,
                transaction_type='challenge',
                amount=points,
                description=f'Desafio: {instance.challenge.title}',
                balance_after=profile.total_points
            )


# Helper function for daily login streak
def update_login_streak(user):
    """Update user's login streak - call this from authentication views"""
    profile = user.user_profiles.first()
    if not profile:
        return
    
    now = timezone.now().date()
    
    # Simple streak logic - award 10 points per consecutive day
    streak_points = 10
    profile.total_points += streak_points
    profile.save()
    
    PointTransaction.objects.create(
        user=user,
        transaction_type='bonus',
        amount=streak_points,
        description='Login diário',
        balance_after=profile.total_points
    )


# Helper function to award experience points
def award_experience_points(user, points, activity_type):
    """Award experience points for various activities"""
    profile = user.user_profiles.first()
    if not profile:
        return
    
    profile.total_points += points
    profile.save()
    
    PointTransaction.objects.create(
        user=user,
        transaction_type='bonus',
        amount=points,
        description=f'XP: {activity_type}',
        balance_after=profile.total_points
    )
