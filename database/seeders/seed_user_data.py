#!/usr/bin/env python3
"""
Seeder for user-related data (user profiles, follows, activities, notifications).
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
import json

# Add the project root to Python path
sys.path.append('/app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from core.models import UserProfile, UserFollow, UserActivity, Notification
from core.models import Team, Player


def seed_user_data():
    """Create sample user profiles, follows, activities and notifications"""
    
    print("🚀 Creating user-related data...")
    
    with transaction.atomic():
        # Get users
        users = list(User.objects.all())
        if not users:
            print("❌ No users found. Please run user seeder first.")
            return
        
        # Create User Profiles
        print("👤 Creating user profiles...")
        profiles_created = 0
        for user in users:
            # Skip if profile already exists
            if hasattr(user, 'userprofile'):
                continue
                
            profile = UserProfile.objects.create(
                user=user,
                bio=random.choice([
                    f"Apaixonado por futebol desde criança. Torço para {random.choice(['Flamengo', 'São Paulo', 'Palmeiras', 'Corinthians'])}!",
                    "Analista de futebol e apostador. Sempre buscando as melhores oportunidades.",
                    "Ex-jogador profissional. Agora compartilho conhecimento sobre o esporte que amo.",
                    "Estatístico e data scientist. Uso dados para entender o futebol.",
                    "Jornalista esportivo especializado em futebol brasileiro e internacional."
                ]),
                birth_date=datetime.now().date() - timedelta(days=random.randint(18*365, 60*365)),
                location=random.choice([
                    'São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 
                    'Porto Alegre, RS', 'Salvador, BA', 'Fortaleza, CE',
                    'Brasília, DF', 'Curitiba, PR', 'Recife, PE', 'Manaus, AM'
                ]),
                phone=f"+55{random.randint(11, 99)}{random.randint(10000000, 99999999)}",
                preferred_language=random.choice(['pt-BR', 'en-US', 'es-ES']),
                timezone=random.choice(['America/Sao_Paulo', 'America/New_York', 'Europe/Madrid']),
                notification_preferences={
                    'email_notifications': random.choice([True, False]),
                    'push_notifications': random.choice([True, False]),
                    'sms_notifications': random.choice([True, False]),
                    'match_alerts': random.choice([True, False]),
                    'prediction_reminders': random.choice([True, False])
                },
                privacy_settings={
                    'profile_visibility': random.choice(['public', 'friends', 'private']),
                    'show_activities': random.choice([True, False]),
                    'show_predictions': random.choice([True, False])
                },
                is_verified=random.choice([True, False]) if random.random() < 0.2 else False
            )
            profiles_created += 1
        
        print(f"✅ Created {profiles_created} user profiles")
        
        # Create User Follows
        print("👥 Creating user follows...")
        follows_created = 0
        for _ in range(min(100, len(users) * 3)):  # Each user follows ~3 others on average
            follower = random.choice(users)
            followed = random.choice(users)
            
            # Don't follow yourself
            if follower == followed:
                continue
                
            # Don't create duplicate follows
            if UserFollow.objects.filter(follower=follower, followed=followed).exists():
                continue
            
            follow = UserFollow.objects.create(
                follower=follower,
                followed=followed,
                created_at=datetime.now() - timedelta(days=random.randint(1, 180))
            )
            follows_created += 1
        
        print(f"✅ Created {follows_created} user follows")
        
        # Create User Activities
        print("📱 Creating user activities...")
        activities_created = 0
        activity_types = [
            'profile_update', 'prediction_made', 'match_watched', 'article_shared',
            'poll_voted', 'comment_posted', 'team_followed', 'player_favorited',
            'achievement_unlocked', 'challenge_completed'
        ]
        
        teams = list(Team.objects.all()[:10])
        players = list(Player.objects.all()[:20])
        
        for _ in range(300):  # Create 300 activities
            user = random.choice(users)
            activity_type = random.choice(activity_types)
            
            # Generate activity details based on type
            details = {}
            if activity_type == 'team_followed' and teams:
                details['team_id'] = random.choice(teams).id
                details['team_name'] = random.choice(teams).name
            elif activity_type == 'player_favorited' and players:
                details['player_id'] = random.choice(players).id
                details['player_name'] = random.choice(players).name
            elif activity_type == 'prediction_made':
                details['confidence'] = random.randint(60, 95)
                details['match_type'] = random.choice(['league', 'cup', 'international'])
            elif activity_type == 'achievement_unlocked':
                details['achievement_name'] = random.choice([
                    'First Prediction', 'Perfect Week', 'Top Predictor', 'Social Butterfly'
                ])
            
            activity = UserActivity.objects.create(
                user=user,
                activity_type=activity_type,
                description=f"User {user.username} performed {activity_type}",
                details=details,
                timestamp=datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            activities_created += 1
        
        print(f"✅ Created {activities_created} user activities")
        
        # Create Notifications
        print("🔔 Creating notifications...")
        notifications_created = 0
        notification_types = [
            'match_reminder', 'prediction_result', 'new_follower', 'mention',
            'achievement', 'challenge_invite', 'system_update', 'promotion'
        ]
        
        for _ in range(200):  # Create 200 notifications
            user = random.choice(users)
            notification_type = random.choice(notification_types)
            
            # Generate titles and messages based on type
            title_map = {
                'match_reminder': 'Lembrete de Partida',
                'prediction_result': 'Resultado da Previsão',
                'new_follower': 'Novo Seguidor',
                'mention': 'Você foi mencionado',
                'achievement': 'Conquista Desbloqueada',
                'challenge_invite': 'Convite para Desafio',
                'system_update': 'Atualização do Sistema',
                'promotion': 'Oferta Especial'
            }
            
            message_map = {
                'match_reminder': f"A partida {random.choice(['Flamengo x Vasco', 'São Paulo x Palmeiras', 'Real Madrid x Barcelona'])} começará em 1 hora!",
                'prediction_result': f"Sua previsão estava {'correta' if random.choice([True, False]) else 'incorreta'}. Pontuação: {random.randint(0, 100)}",
                'new_follower': f"{random.choice(users).username} começou a seguir você!",
                'mention': f"Você foi mencionado em um comentário por {random.choice(users).username}",
                'achievement': f"Parabéns! Você desbloqueou a conquista '{random.choice(['Analista Expert', 'Torcedor Fiel', 'Preditor Master'])}'",
                'challenge_invite': f"{random.choice(users).username} te convidou para um desafio de previsões",
                'system_update': "Nova versão disponível com melhorias na análise de dados",
                'promotion': "Upgrade para Premium com 50% de desconto! Oferta limitada."
            }
            
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title_map[notification_type],
                message=message_map[notification_type],
                is_read=random.choice([True, False]),
                created_at=datetime.now() - timedelta(
                    days=random.randint(0, 15),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )
            notifications_created += 1
        
        print(f"✅ Created {notifications_created} notifications")
        
        print('\n🎉 User data seeded successfully!')
        
        # Display summary
        print(f'\n📊 User Data Summary:')
        print(f'   User Profiles: {UserProfile.objects.count()}')
        print(f'   - Verified: {UserProfile.objects.filter(is_verified=True).count()}')
        print(f'   User Follows: {UserFollow.objects.count()}')
        print(f'   User Activities: {UserActivity.objects.count()}')
        print(f'   Notifications: {Notification.objects.count()}')
        print(f'   - Unread: {Notification.objects.filter(is_read=False).count()}')


if __name__ == '__main__':
    seed_user_data()
