"""
Seeder for WhatsApp Integration test data.
Creates test WhatsApp users, sessions, and messages for development.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import json
from whatsapp_integration.models import WhatsAppUser, WhatsAppSession, WhatsAppMessage


def create_whatsapp_users():
    """Create test WhatsApp users"""
    print("🚀 Creating WhatsApp test users...")
    
    # Clear existing data
    WhatsAppMessage.objects.all().delete()
    WhatsAppSession.objects.all().delete()
    WhatsAppUser.objects.all().delete()
    
    # Test phone numbers (fake Brazilian numbers)
    phone_numbers = [
        '+5511987654321',
        '+5511987654322',
        '+5511987654323',
        '+5511987654324',
        '+5511987654325',
        '+5521987654321',
        '+5521987654322',
        '+5531987654321',
        '+5541987654321',
        '+5551987654321',
    ]
    
    display_names = [
        'João da Silva',
        'Maria Santos',
        'Pedro Oliveira',
        'Ana Costa',
        'Carlos Ferreira',
        'Lucia Rodrigues',
        'Rafael Almeida',
        'Patricia Lima',
        'Fernando Pereira',
        'Juliana Carvalho',
    ]
    
    whatsapp_users = []
    
    for i, (phone, name) in enumerate(zip(phone_numbers, display_names)):
        # Get existing user if available
        try:
            django_user = User.objects.filter(is_superuser=False).order_by('?').first()
        except:
            django_user = None
        
        # Create WhatsApp user
        whatsapp_user = WhatsAppUser.objects.create(
            phone_number=phone,
            display_name=name,
            user=django_user if i % 3 == 0 else None,  # Link some users to Django users
            is_premium=i < 3,  # First 3 are premium
            subscription_plan='premium' if i < 3 else 'free',
            daily_queries_count=random.randint(0, 10 if i < 3 else 5),
            last_query_date=timezone.now().date() - timedelta(days=random.randint(0, 7))
        )
        whatsapp_users.append(whatsapp_user)
        
        print(f"  ✅ Created WhatsApp user: {name} ({phone}) - {'Premium' if whatsapp_user.is_premium else 'Free'}")
    
    return whatsapp_users


def create_whatsapp_sessions(whatsapp_users):
    """Create test WhatsApp sessions"""
    print("\n🔗 Creating WhatsApp sessions...")
    
    sessions = []
    
    for i, user in enumerate(whatsapp_users[:7]):  # Create sessions for first 7 users
        session = WhatsAppSession.objects.create(
            whatsapp_user=user,
            session_id=f"session_{user.phone_number.replace('+', '').replace(' ', '')}_{i}",
            context_data={
                'last_topic': random.choice(['teams', 'matches', 'players', 'help']),
                'favorite_team': random.choice(['Palmeiras', 'Flamengo', 'Corinthians', 'São Paulo']),
                'language': 'pt-BR',
                'timezone': 'America/Sao_Paulo'
            },
            is_active=i < 5,  # First 5 sessions are active
            last_activity=timezone.now() - timedelta(minutes=random.randint(1, 1440))
        )
        sessions.append(session)
        
        print(f"  ✅ Created session for {user.display_name} - {'Active' if session.is_active else 'Inactive'}")
    
    return sessions


def create_whatsapp_messages(whatsapp_users):
    """Create test WhatsApp messages"""
    print("\n💬 Creating WhatsApp messages...")
    
    # Sample incoming messages
    incoming_messages = [
        "Oi! Como está o Palmeiras?",
        "Próximos jogos do Flamengo",
        "Resultado do último jogo",
        "Estatísticas do Neymar",
        "Como funciona o premium?",
        "PREMIUM",
        "Ajuda",
        "Menu",
        "Quais times vocês acompanham?",
        "Tabela do brasileirão",
        "Gols do Ronaldinho",
        "Melhor jogador brasileiro",
        "Copa do mundo 2026",
        "Champions League hoje",
        "Classificação libertadores"
    ]
    
    # Sample outgoing messages
    outgoing_messages = [
        "Olá! Sou o assistente Mark Foot! 👋",
        "🏆 Palmeiras está em 2º lugar no Brasileirão",
        "⚽ Próximo jogo: Flamengo vs Santos - 19/03 às 16h",
        "📊 Últimos resultados carregados com sucesso!",
        "🤖 Como posso ajudar com informações de futebol?",
        "🏆 Mark Foot Premium - Consultas ilimitadas por R$ 19,90/mês",
        "⚠️ Limite de consultas diárias atingido! Considere o Premium.",
        "✅ Informações atualizadas com sucesso!",
        "📋 Digite 'AJUDA' para ver todas as opções disponíveis",
        "⚽ Posso ajudar com times, jogadores, jogos e resultados!"
    ]
    
    created_count = 0
    
    for user in whatsapp_users:
        # Create 3-8 messages per user
        message_count = random.randint(3, 8)
        
        for i in range(message_count):
            is_incoming = random.choice([True, False])
            
            message = WhatsAppMessage.objects.create(
                whatsapp_user=user,
                message_id=f"msg_{user.phone_number.replace('+', '')}_{i}_{random.randint(1000, 9999)}",
                message_type='text',
                content=random.choice(incoming_messages if is_incoming else outgoing_messages),
                is_incoming=is_incoming,
                processed=True,
                timestamp=timezone.now() - timedelta(
                    hours=random.randint(1, 168),  # Last week
                    minutes=random.randint(0, 59)
                )
            )
            created_count += 1
    
    print(f"  ✅ Created {created_count} test messages")


def create_premium_subscription_examples():
    """Create examples of premium subscription flows"""
    print("\n💰 Creating premium subscription examples...")
    
    # Find premium users
    premium_users = WhatsAppUser.objects.filter(is_premium=True)
    
    for user in premium_users[:2]:  # First 2 premium users
        # Premium activation message
        WhatsAppMessage.objects.create(
            whatsapp_user=user,
            message_id=f"premium_activation_{user.phone_number.replace('+', '')}",
            message_type='text',
            content="PREMIUM",
            is_incoming=True,
            processed=True,
            timestamp=timezone.now() - timedelta(days=random.randint(1, 30))
        )
        
        # Premium welcome message
        WhatsAppMessage.objects.create(
            whatsapp_user=user,
            message_id=f"premium_welcome_{user.phone_number.replace('+', '')}",
            message_type='text',
            content="🎉 Parabéns! Você agora é Premium! Consultas ilimitadas liberadas!",
            is_incoming=False,
            processed=True,
            timestamp=timezone.now() - timedelta(days=random.randint(1, 30))
        )
        
        print(f"  ✅ Created premium flow for {user.display_name}")


def main():
    """Main seeder function"""
    print("🌱 Starting WhatsApp Integration Seeder\n")
    
    try:
        # Create test data
        whatsapp_users = create_whatsapp_users()
        sessions = create_whatsapp_sessions(whatsapp_users)
        create_whatsapp_messages(whatsapp_users)
        create_premium_subscription_examples()
        
        print(f"\n✅ WhatsApp Integration seeding completed successfully!")
        print(f"   📱 {len(whatsapp_users)} WhatsApp users created")
        print(f"   🔗 {len(sessions)} sessions created")
        print(f"   💬 Messages and conversations created")
        print(f"   💰 Premium subscription examples added")
        
        # Show statistics
        print(f"\n📊 Statistics:")
        print(f"   Free users: {WhatsAppUser.objects.filter(is_premium=False).count()}")
        print(f"   Premium users: {WhatsAppUser.objects.filter(is_premium=True).count()}")
        print(f"   Active sessions: {WhatsAppSession.objects.filter(is_active=True).count()}")
        print(f"   Total messages: {WhatsAppMessage.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
