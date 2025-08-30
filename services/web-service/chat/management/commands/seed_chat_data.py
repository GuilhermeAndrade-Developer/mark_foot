"""
Seeder for chat module data.
Creates professional development data for chat rooms and messages.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed chat data for development'

    def handle(self, *args, **options):
        self.stdout.write('💬 Seeding chat data...')
        
        # Create chat rooms
        rooms_created = self.create_chat_rooms()
        
        # Create messages
        messages_created = self.create_messages()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Chat data seeded:\n'
                f'   🏠 Chat Rooms: {rooms_created}\n'
                f'   💬 Messages: {messages_created}'
            )
        )

    def create_chat_rooms(self):
        """Create chat rooms"""
        users = list(User.objects.filter(is_active=True))
        if not users:
            return 0

        rooms_data = [
            {
                'name': 'Geral',
                'description': 'Chat geral sobre futebol',
                'room_type': 'public',
                'max_participants': 100,
                'is_active': True
            },
            {
                'name': 'Brasileirão 2024',
                'description': 'Discussões sobre o Campeonato Brasileiro',
                'room_type': 'public',
                'max_participants': 50,
                'is_active': True
            },
            {
                'name': 'Champions League',
                'description': 'Tudo sobre a Liga dos Campeões',
                'room_type': 'public',
                'max_participants': 75,
                'is_active': True
            },
            {
                'name': 'Análises Táticas',
                'description': 'Discussões técnicas sobre futebol',
                'room_type': 'restricted',
                'max_participants': 25,
                'is_active': True
            },
            {
                'name': 'Fantasy Football',
                'description': 'Dicas e discussões sobre fantasy',
                'room_type': 'public',
                'max_participants': 40,
                'is_active': True
            }
        ]

        created_count = 0
        for room_data in rooms_data:
            admin = random.choice(users)
            
            room, created = ChatRoom.objects.get_or_create(
                name=room_data['name'],
                defaults={
                    **room_data,
                    'created_by': admin,
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 15))
                }
            )
            
            if created:
                created_count += 1
                
                # Add participants
                participant_count = random.randint(5, min(15, len(users)))
                participants = random.sample(users, participant_count)
                
                for participant in participants:
                    room.participants.add(participant)

        return created_count

    def create_messages(self):
        """Create sample messages"""
        users = list(User.objects.filter(is_active=True))
        rooms = ChatRoom.objects.filter(is_active=True)
        
        if not users or not rooms.exists():
            return 0

        sample_messages = [
            "Alguém viu o jogo de ontem?",
            "Que jogada incrível!",
            "O técnico acertou na substituição",
            "Análise tática interessante",
            "Quem vocês acham que vai ganhar?",
            "Estatísticas impressionantes",
            "Concordo com a análise",
            "Excelente discussão!",
            "Não concordo, mas respeito",
            "Dados muito interessantes",
            "Ótima observação!",
            "Vamos ver como evolui",
            "Temporada está emocionante",
            "Melhor campeonato dos últimos anos",
            "Que lance polêmico!",
            "VAR ajudou na decisão",
            "Arbitragem controversa",
            "Jogador em grande fase",
            "Time evoluindo taticamente",
            "Contratação acertada"
        ]

        created_count = 0
        
        for room in rooms:
            participants = list(room.participants.all())
            if not participants:
                continue
                
            # Create 20-50 messages per room
            message_count = random.randint(20, 50)
            
            for _ in range(message_count):
                author = random.choice(participants)
                content = random.choice(sample_messages)
                
                Message.objects.create(
                    room=room,
                    author=author,
                    content=content,
                    created_at=timezone.now() - timedelta(
                        days=random.randint(0, 7),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    is_system_message=False
                )
                created_count += 1

        return created_count
