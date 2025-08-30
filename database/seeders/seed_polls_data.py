"""
Seeder for polls module data.
Replaces hardcoded polls with professional development seeds.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from polls.models import Poll, PollOption, PollVote
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed polls data for development'

    def handle(self, *args, **options):
        self.stdout.write('🗳️  Seeding polls data...')
        
        # Create polls
        polls_created = self.create_polls()
        
        # Create votes for polls
        votes_created = self.create_votes()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Polls data seeded:\n'
                f'   📊 Polls: {polls_created}\n'
                f'   🗳️  Votes: {votes_created}'
            )
        )

    def create_polls(self):
        """Create sample polls"""
        # Get users for poll authors
        authors = list(User.objects.filter(is_active=True))
        if not authors:
            self.stdout.write('⚠️  No users found for poll authors')
            return 0

        polls_data = [
            {
                'title': 'Melhor jogador brasileiro na atualidade?',
                'question': 'Considerando performance, títulos e consistência, quem é o melhor jogador brasileiro atuando hoje?',
                'description': 'Vote no jogador brasileiro que você considera o melhor no momento atual.',
                'status': 'active',
                'is_featured': True,
                'poll_type': 'single_choice',
                'options': [
                    'Vinicius Jr.',
                    'Casemiro', 
                    'Alisson',
                    'Marquinhos',
                    'Raphinha'
                ]
            },
            {
                'title': 'Melhor formação tática para o futebol moderno?',
                'question': 'Qual formação tática você considera mais eficaz no futebol atual?',
                'description': 'Analise as formações mais utilizadas pelos grandes clubes atualmente.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    '4-3-3',
                    '4-2-3-1', 
                    '3-5-2',
                    '4-4-2',
                    '3-4-3',
                    '4-1-4-1'
                ]
            },
            {
                'title': 'Favorito para o título do Brasileirão 2024?',
                'question': 'Qual time tem mais chances de conquistar o Campeonato Brasileiro este ano?',
                'description': 'Vote no seu favorito para levantar a taça do Brasileirão.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    'Flamengo',
                    'Palmeiras',
                    'São Paulo',
                    'Corinthians',
                    'Atlético Mineiro',
                    'Internacional'
                ]
            },
            {
                'title': 'Melhor técnico brasileiro em atividade?',
                'question': 'Quem você considera o melhor treinador brasileiro atualmente?',
                'description': 'Vote no técnico brasileiro que mais admira pelo trabalho atual.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    'Abel Ferreira',
                    'Renato Gaúcho',
                    'Dorival Júnior',
                    'Fernando Diniz',
                    'Mano Menezes'
                ]
            },
            {
                'title': 'VAR no futebol brasileiro: sua opinião?',
                'question': 'Como você avalia o uso do VAR no Campeonato Brasileiro?',
                'description': 'O VAR tem sido tema de muitos debates. Dê sua opinião sobre sua implementação.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    'Excelente, trouxe mais justiça',
                    'Bom, mas precisa melhorar',
                    'Regular, muitas polêmicas ainda',
                    'Ruim, muito demorado',
                    'Péssimo, deveria ser removido'
                ]
            },
            {
                'title': 'Posição mais importante no futebol moderno?',
                'question': 'Qual posição você considera mais crucial no futebol atual?',
                'description': 'Considerando a evolução tática do futebol, vote na posição mais importante.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    'Goleiro',
                    'Zagueiro Central',
                    'Lateral/Ala',
                    'Volante',
                    'Meia Atacante',
                    'Centroavante'
                ]
            },
            {
                'title': 'Melhor geração da Seleção Brasileira?',
                'question': 'Qual geração da Seleção Brasileira você considera a melhor da história?',
                'description': 'Vote na geração que marcou época no futebol mundial.',
                'status': 'closed',
                'poll_type': 'single_choice',
                'options': [
                    'Brasil 1970 (Pelé)',
                    'Brasil 1982 (Zico, Sócrates)',
                    'Brasil 1994 (Romário, Bebeto)',
                    'Brasil 1998-2002 (Ronaldo, Ronaldinho)',
                    'Brasil 2002 (Ronaldo, Rivaldo, Ronaldinho)'
                ]
            },
            {
                'title': 'Maior clássico do futebol brasileiro?',
                'question': 'Qual você considera o maior clássico do futebol nacional?',
                'description': 'Vote no confronto que mais emociona e mobiliza o país.',
                'status': 'active',
                'poll_type': 'single_choice',
                'options': [
                    'Fla-Flu',
                    'Corinthians x Palmeiras',
                    'Grêmio x Internacional',
                    'Atlético-MG x Cruzeiro',
                    'Santos x São Paulo'
                ]
            },
            # Multiple choice poll
            {
                'title': 'Principais problemas do futebol brasileiro? (múltipla escolha)',
                'question': 'Quais são os maiores desafios que o futebol brasileiro enfrenta atualmente?',
                'description': 'Selecione todos os problemas que você considera relevantes.',
                'status': 'active',
                'poll_type': 'multiple_choice',
                'options': [
                    'Má gestão dos clubes',
                    'Calendário sobrecarregado',
                    'Falta de investimento na base',
                    'Arbitragem deficiente',
                    'Violência nos estádios',
                    'Preços altos dos ingressos'
                ]
            }
        ]

        created_count = 0
        for poll_data in polls_data:
            options = poll_data.pop('options')
            author = random.choice(authors)
            
            # Set dates
            created_at = timezone.now() - timedelta(days=random.randint(1, 30))
            
            if poll_data['status'] == 'closed':
                ends_at = timezone.now() - timedelta(days=random.randint(1, 7))
            else:
                ends_at = timezone.now() + timedelta(days=random.randint(7, 30))

            poll, created = Poll.objects.get_or_create(
                title=poll_data['title'],
                defaults={
                    **poll_data,
                    'author': author,
                    'created_at': created_at,
                    'ends_at': ends_at,
                    'total_votes': 0,  # Will be updated when creating votes
                    'views': random.randint(500, 5000)
                }
            )
            
            if created:
                created_count += 1
                
                # Create options for the poll
                for i, option_text in enumerate(options):
                    PollOption.objects.create(
                        poll=poll,
                        text=option_text,
                        order=i,
                        votes=0,  # Will be updated when creating votes
                        percentage=0.0
                    )

        return created_count

    def create_votes(self):
        """Create sample votes for polls"""
        users = list(User.objects.filter(is_active=True))
        active_polls = Poll.objects.filter(status='active')
        
        if not users or not active_polls.exists():
            return 0

        votes_created = 0
        
        for poll in active_polls:
            options = list(poll.options.all())
            if not options:
                continue

            # Generate random number of votes for this poll
            vote_count = random.randint(50, 1000)
            
            for _ in range(vote_count):
                user = random.choice(users)
                
                # Check if user already voted
                if PollVote.objects.filter(poll=poll, user=user).exists():
                    continue

                if poll.poll_type == 'multiple_choice':
                    # For multiple choice, select 1-3 random options
                    selected_options = random.sample(options, random.randint(1, min(3, len(options))))
                else:
                    # For single choice, select 1 option
                    selected_options = [random.choice(options)]

                # Create vote
                vote = PollVote.objects.create(
                    poll=poll,
                    user=user,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 7))
                )
                
                # Add selected options
                vote.selected_options.set(selected_options)
                votes_created += 1

            # Update poll statistics
            self.update_poll_stats(poll)

        return votes_created

    def update_poll_stats(self, poll):
        """Update poll vote counts and percentages"""
        total_votes = poll.votes.count()
        poll.total_votes = total_votes
        poll.save()

        if total_votes > 0:
            for option in poll.options.all():
                option_votes = option.votes_received.count()
                option.votes = option_votes
                option.percentage = round((option_votes / total_votes) * 100, 2)
                option.save()
