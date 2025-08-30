"""
Seeder for core football data (teams, competitions, players).
Replaces hardcoded data with configurable development seeds.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Team, Competition, Player, Match
from django.utils import timezone
from datetime import timedelta, date
import random


class Command(BaseCommand):
    help = 'Seed core football data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick seed with minimal data',
        )
        parser.add_argument(
            '--teams-only',
            action='store_true',
            help='Only create teams (no players/matches)',
        )

    def handle(self, *args, **options):
        self.stdout.write('⚽ Seeding core football data...')
        
        with transaction.atomic():
            # Create competitions
            competitions_created = self.create_competitions()
            
            # Create teams
            teams_created = self.create_teams(quick=options['quick'])
            
            if not options['teams_only']:
                # Create players
                players_created = self.create_players(quick=options['quick'])
                
                # Create matches
                matches_created = self.create_matches(quick=options['quick'])
            else:
                players_created = 0
                matches_created = 0

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Core data seeded:\n'
                f'   🏆 Competitions: {competitions_created}\n'
                f'   ⚽ Teams: {teams_created}\n'
                f'   🏃 Players: {players_created}\n'
                f'   📊 Matches: {matches_created}'
            )
        )

    def create_competitions(self):
        """Create basic competitions"""
        competitions_data = [
            {
                'name': 'Campeonato Brasileiro Série A',
                'code': 'BRA1',
                'country': 'Brazil',
                'type': 'league',
                'current_season': '2024',
                'is_active': True
            },
            {
                'name': 'UEFA Champions League',
                'code': 'CL',
                'country': 'Europe',
                'type': 'cup',
                'current_season': '2024-25',
                'is_active': True
            },
            {
                'name': 'Premier League',
                'code': 'PL',
                'country': 'England',
                'type': 'league',
                'current_season': '2024-25',
                'is_active': True
            },
            {
                'name': 'La Liga',
                'code': 'LL',
                'country': 'Spain',
                'type': 'league',
                'current_season': '2024-25',
                'is_active': True
            },
            {
                'name': 'Copa do Brasil',
                'code': 'CDB',
                'country': 'Brazil',
                'type': 'cup',
                'current_season': '2024',
                'is_active': True
            }
        ]

        created_count = 0
        for comp_data in competitions_data:
            competition, created = Competition.objects.get_or_create(
                code=comp_data['code'],
                defaults=comp_data
            )
            if created:
                created_count += 1

        return created_count

    def create_teams(self, quick=False):
        """Create teams with Brazilian and international clubs"""
        brazilian_teams = [
            ('Flamengo', 'FLA', 'Rio de Janeiro', 'Brazil'),
            ('São Paulo', 'SAO', 'São Paulo', 'Brazil'),
            ('Palmeiras', 'PAL', 'São Paulo', 'Brazil'),
            ('Corinthians', 'COR', 'São Paulo', 'Brazil'),
            ('Santos', 'SAN', 'Santos', 'Brazil'),
            ('Grêmio', 'GRE', 'Porto Alegre', 'Brazil'),
            ('Internacional', 'INT', 'Porto Alegre', 'Brazil'),
            ('Atlético Mineiro', 'ATM', 'Belo Horizonte', 'Brazil'),
            ('Cruzeiro', 'CRU', 'Belo Horizonte', 'Brazil'),
            ('Vasco da Gama', 'VAS', 'Rio de Janeiro', 'Brazil'),
            ('Botafogo', 'BOT', 'Rio de Janeiro', 'Brazil'),
            ('Fluminense', 'FLU', 'Rio de Janeiro', 'Brazil'),
        ]

        international_teams = [
            ('Real Madrid', 'RMA', 'Madrid', 'Spain'),
            ('Barcelona', 'BAR', 'Barcelona', 'Spain'),
            ('Manchester City', 'MCI', 'Manchester', 'England'),
            ('Liverpool', 'LIV', 'Liverpool', 'England'),
            ('Paris Saint-Germain', 'PSG', 'Paris', 'France'),
            ('Bayern München', 'BAY', 'Munich', 'Germany'),
            ('Juventus', 'JUV', 'Turin', 'Italy'),
            ('AC Milan', 'MIL', 'Milan', 'Italy'),
            ('Chelsea', 'CHE', 'London', 'England'),
            ('Arsenal', 'ARS', 'London', 'England'),
        ]

        teams_to_create = brazilian_teams
        if not quick:
            teams_to_create.extend(international_teams)

        created_count = 0
        for name, code, city, country in teams_to_create:
            team, created = Team.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'city': city,
                    'country': country,
                    'founded_year': random.randint(1900, 1950),
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        return created_count

    def create_players(self, quick=False):
        """Create players for teams (replacing hardcoded player list)"""
        teams = Team.objects.all()
        if not teams.exists():
            return 0

        # Brazilian player names
        brazilian_players = [
            ('Gabriel', 'Silva', 'Forward'),
            ('João', 'Santos', 'Midfielder'),
            ('Pedro', 'Oliveira', 'Defender'),
            ('Rafael', 'Costa', 'Goalkeeper'),
            ('Lucas', 'Ferreira', 'Forward'),
            ('Mateus', 'Rodrigues', 'Midfielder'),
            ('Carlos', 'Almeida', 'Defender'),
            ('Diego', 'Lima', 'Forward'),
            ('Felipe', 'Pereira', 'Midfielder'),
            ('Bruno', 'Carvalho', 'Defender'),
            ('Vinicius', 'Machado', 'Forward'),
            ('Thiago', 'Barbosa', 'Midfielder'),
            ('Rodrigo', 'Ribeiro', 'Defender'),
            ('André', 'Martins', 'Goalkeeper'),
            ('Gustavo', 'Araújo', 'Forward'),
        ]

        # International player names
        international_players = [
            ('Lionel', 'Messi', 'Forward'),
            ('Cristiano', 'Ronaldo', 'Forward'),
            ('Kylian', 'Mbappé', 'Forward'),
            ('Erling', 'Haaland', 'Forward'),
            ('Kevin', 'De Bruyne', 'Midfielder'),
            ('Mohamed', 'Salah', 'Forward'),
            ('Robert', 'Lewandowski', 'Forward'),
            ('Luka', 'Modrić', 'Midfielder'),
            ('Virgil', 'van Dijk', 'Defender'),
            ('Sadio', 'Mané', 'Forward'),
            ('Harry', 'Kane', 'Forward'),
            ('Sergio', 'Ramos', 'Defender'),
            ('Karim', 'Benzema', 'Forward'),
            ('N\'Golo', 'Kanté', 'Midfielder'),
            ('Neymar', 'Jr.', 'Forward'),
        ]

        players_to_create = brazilian_players
        if not quick:
            players_to_create.extend(international_players)

        created_count = 0
        players_per_team = 5 if quick else 10

        for team in teams:
            # Assign random players to each team
            team_players = random.sample(players_to_create, min(players_per_team, len(players_to_create)))
            
            for first_name, last_name, position in team_players:
                # Create unique player name for this team
                full_name = f"{first_name} {last_name}"
                
                player, created = Player.objects.get_or_create(
                    name=full_name,
                    team=team,
                    defaults={
                        'position': position,
                        'age': random.randint(18, 35),
                        'nationality': team.country,
                        'shirt_number': random.randint(1, 99),
                        'market_value': random.randint(1000000, 100000000),
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1

        return created_count

    def create_matches(self, quick=False):
        """Create sample matches"""
        teams = list(Team.objects.all())
        competitions = list(Competition.objects.all())
        
        if len(teams) < 2 or not competitions:
            return 0

        match_count = 10 if quick else 25
        created_count = 0

        for _ in range(match_count):
            # Select random teams and competition
            home_team, away_team = random.sample(teams, 2)
            competition = random.choice(competitions)
            
            # Create match date (last 30 days or next 15 days)
            if random.choice([True, False]):
                # Past match
                match_date = timezone.now() - timedelta(days=random.randint(1, 30))
                status = 'finished'
                home_score = random.randint(0, 4)
                away_score = random.randint(0, 4)
            else:
                # Future match
                match_date = timezone.now() + timedelta(days=random.randint(1, 15))
                status = 'scheduled'
                home_score = None
                away_score = None

            match = Match.objects.create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                match_date=match_date,
                status=status,
                home_score=home_score,
                away_score=away_score,
                round_number=random.randint(1, 38),
                season='2024'
            )
            created_count += 1

        return created_count
