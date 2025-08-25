from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Player, PlayerStatistics, PlayerTransfer
from data_management.collectors.player_collector import PlayerDataCollector
import json


class Command(BaseCommand):
    help = 'Advanced player data analysis and reporting'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['player-report', 'missing-data', 'data-quality', 'team-roster', 'nationality-stats'],
            default='player-report',
            help='Analysis action to perform'
        )
        
        parser.add_argument(
            '--player-id',
            type=str,
            help='Specific player external ID for detailed report'
        )
        
        parser.add_argument(
            '--team',
            type=str,
            help='Team name for roster analysis'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        self.stdout.write(
            self.style.SUCCESS('📊 Mark Foot - Advanced Player Analytics')
        )
        self.stdout.write('=' * 60)
        
        if action == 'player-report':
            self.generate_player_report(options)
        elif action == 'missing-data':
            self.analyze_missing_data()
        elif action == 'data-quality':
            self.analyze_data_quality()
        elif action == 'team-roster':
            self.analyze_team_roster(options)
        elif action == 'nationality-stats':
            self.analyze_nationality_stats()

    def generate_player_report(self, options):
        """Generate detailed report for a specific player"""
        player_id = options.get('player_id')
        
        if not player_id:
            self.stdout.write(
                self.style.ERROR('❌ Player ID required. Use --player-id "external_id"')
            )
            return
        
        try:
            player = Player.objects.get(external_id=player_id)
        except Player.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Player with ID {player_id} not found')
            )
            return
        
        self.stdout.write(f'\n🌟 Detailed Player Report')
        self.stdout.write('-' * 50)
        
        # Basic Information
        self.stdout.write(f'\n📋 Basic Information:')
        self.stdout.write(f'  • Name: {player.name}')
        self.stdout.write(f'  • Short Name: {player.short_name or "N/A"}')
        self.stdout.write(f'  • External ID: {player.external_id}')
        self.stdout.write(f'  • Team: {player.team.name if player.team else "No Team"}')
        self.stdout.write(f'  • Position: {player.position or "Unknown"}')
        self.stdout.write(f'  • Position Category: {player.get_position_category_display() or "Unknown"}')
        self.stdout.write(f'  • Nationality: {player.nationality or "Unknown"}')
        self.stdout.write(f'  • Date of Birth: {player.date_of_birth or "Unknown"}')
        self.stdout.write(f'  • Age: {player.age or "Unknown"}')
        self.stdout.write(f'  • Gender: {player.gender}')
        self.stdout.write(f'  • Status: {player.status}')
        
        # Physical Information
        self.stdout.write(f'\n🏃 Physical Information:')
        self.stdout.write(f'  • Height: {player.height or "N/A"}')
        self.stdout.write(f'  • Weight: {player.weight or "N/A"}')
        
        # Contract Information
        self.stdout.write(f'\n💰 Contract Information:')
        self.stdout.write(f'  • Wage: {player.wage or "N/A"}')
        
        # Media Information
        self.stdout.write(f'\n🖼️ Media Information:')
        self.stdout.write(f'  • Photo URL: {"✅ Available" if player.photo_url else "❌ Not Available"}')
        self.stdout.write(f'  • Cutout URL: {"✅ Available" if player.cutout_url else "❌ Not Available"}')
        
        # Description
        if player.description:
            self.stdout.write(f'\n📝 Description:')
            description = player.description[:200] + "..." if len(player.description) > 200 else player.description
            self.stdout.write(f'  {description}')
        
        # Statistics Summary
        stats_count = PlayerStatistics.objects.filter(player=player).count()
        transfers_count = PlayerTransfer.objects.filter(player=player).count()
        
        self.stdout.write(f'\n📊 Data Summary:')
        self.stdout.write(f'  • Statistics Records: {stats_count}')
        self.stdout.write(f'  • Transfer Records: {transfers_count}')
        self.stdout.write(f'  • Last Sync: {player.last_sync or "Never"}')
        
        # Data Completeness Score
        score = self._calculate_completeness_score(player)
        self.stdout.write(f'  • Data Completeness: {score}% {"🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"}')

    def analyze_missing_data(self):
        """Analyze missing data across all players"""
        self.stdout.write(f'\n🔍 Missing Data Analysis')
        self.stdout.write('-' * 40)
        
        total_players = Player.objects.count()
        
        if total_players == 0:
            self.stdout.write('❌ No players found in database')
            return
        
        # Check missing fields
        missing_fields = {
            'team': Player.objects.filter(team__isnull=True).count(),
            'position': Player.objects.filter(position__exact='').count() + Player.objects.filter(position__isnull=True).count(),
            'nationality': Player.objects.filter(nationality__exact='').count() + Player.objects.filter(nationality__isnull=True).count(),
            'date_of_birth': Player.objects.filter(date_of_birth__isnull=True).count(),
            'height': Player.objects.filter(height__exact='').count() + Player.objects.filter(height__isnull=True).count(),
            'weight': Player.objects.filter(weight__exact='').count() + Player.objects.filter(weight__isnull=True).count(),
            'photo_url': Player.objects.filter(photo_url__exact='').count() + Player.objects.filter(photo_url__isnull=True).count(),
            'description': Player.objects.filter(description__exact='').count() + Player.objects.filter(description__isnull=True).count(),
        }
        
        self.stdout.write(f'\n📊 Missing Data by Field (out of {total_players} players):')
        
        for field, count in missing_fields.items():
            percentage = (count / total_players) * 100
            status = "🔴" if percentage > 50 else "🟡" if percentage > 20 else "🟢"
            self.stdout.write(f'  • {field.replace("_", " ").title()}: {count} ({percentage:.1f}%) {status}')
        
        # Overall completeness
        total_missing = sum(missing_fields.values())
        total_possible = total_players * len(missing_fields)
        completeness = ((total_possible - total_missing) / total_possible) * 100
        
        self.stdout.write(f'\n🎯 Overall Data Completeness: {completeness:.1f}%')

    def analyze_data_quality(self):
        """Analyze data quality issues"""
        self.stdout.write(f'\n🔬 Data Quality Analysis')
        self.stdout.write('-' * 40)
        
        # Duplicate names
        from django.db.models import Count
        duplicate_names = Player.objects.values('name').annotate(
            count=Count('name')
        ).filter(count__gt=1).order_by('-count')
        
        if duplicate_names.exists():
            self.stdout.write(f'\n⚠️ Potential Duplicate Names:')
            for dup in duplicate_names[:10]:
                name = dup['name']
                count = dup['count']
                self.stdout.write(f'  • "{name}": {count} players')
        
        # Invalid ages
        invalid_ages = Player.objects.filter(age__lt=15).count() + Player.objects.filter(age__gt=50).count()
        if invalid_ages > 0:
            self.stdout.write(f'\n⚠️ Players with unusual ages: {invalid_ages}')
        
        # Missing position categories
        missing_categories = Player.objects.filter(
            position__isnull=False
        ).exclude(position__exact='').filter(
            position_category__exact=''
        ).count()
        
        if missing_categories > 0:
            self.stdout.write(f'\n⚠️ Players with position but no category: {missing_categories}')
        
        # Players without teams
        no_team = Player.objects.filter(team__isnull=True).count()
        self.stdout.write(f'\n📊 Players without teams: {no_team}')

    def analyze_team_roster(self, options):
        """Analyze team roster composition"""
        team_name = options.get('team')
        
        if not team_name:
            self.stdout.write(
                self.style.ERROR('❌ Team name required. Use --team "team name"')
            )
            return
        
        # Find team players
        players = Player.objects.filter(
            team__name__icontains=team_name
        )
        
        if not players.exists():
            self.stdout.write(f'❌ No players found for team containing "{team_name}"')
            return
        
        team = players.first().team
        self.stdout.write(f'\n🏆 Team Roster Analysis: {team.name}')
        self.stdout.write('-' * 50)
        
        total_players = players.count()
        self.stdout.write(f'\n📊 Total Players: {total_players}')
        
        # Position distribution
        from django.db.models import Count
        position_dist = players.values('position_category').annotate(
            count=Count('position_category')
        ).order_by('-count')
        
        self.stdout.write(f'\n🎯 Position Distribution:')
        position_names = {
            'GK': 'Goalkeepers',
            'DF': 'Defenders', 
            'MF': 'Midfielders',
            'FW': 'Forwards',
            'SUB': 'Substitutes',
            'COACH': 'Coaches'
        }
        
        for pos in position_dist:
            category = pos['position_category']
            count = pos['count']
            if category:
                name = position_names.get(category, category)
                percentage = (count / total_players) * 100
                self.stdout.write(f'  • {name}: {count} ({percentage:.1f}%)')
        
        # Nationality distribution
        nationality_dist = players.exclude(
            nationality__exact=''
        ).values('nationality').annotate(
            count=Count('nationality')
        ).order_by('-count')[:5]
        
        self.stdout.write(f'\n🌍 Top Nationalities:')
        for nat in nationality_dist:
            nationality = nat['nationality']
            count = nat['count']
            self.stdout.write(f'  • {nationality}: {count} players')

    def analyze_nationality_stats(self):
        """Analyze nationality statistics across all players"""
        self.stdout.write(f'\n🌍 Global Nationality Analysis')
        self.stdout.write('-' * 40)
        
        from django.db.models import Count
        
        # Top nationalities
        nationalities = Player.objects.exclude(
            nationality__exact=''
        ).values('nationality').annotate(
            count=Count('nationality')
        ).order_by('-count')
        
        total_with_nationality = sum(n['count'] for n in nationalities)
        total_players = Player.objects.count()
        
        self.stdout.write(f'\n📊 Players with nationality data: {total_with_nationality}/{total_players}')
        
        self.stdout.write(f'\n🏆 Top 15 Nationalities:')
        for i, nat in enumerate(nationalities[:15], 1):
            nationality = nat['nationality']
            count = nat['count']
            percentage = (count / total_with_nationality) * 100
            self.stdout.write(f'  {i:2d}. {nationality}: {count} players ({percentage:.1f}%)')
        
        # Geographic distribution
        european_countries = [
            'Spain', 'Italy', 'France', 'Germany', 'England', 'Portugal', 
            'Netherlands', 'Belgium', 'Croatia', 'Serbia', 'Poland'
        ]
        
        south_american_countries = [
            'Brazil', 'Argentina', 'Uruguay', 'Colombia', 'Chile', 'Peru', 'Ecuador'
        ]
        
        european_count = Player.objects.filter(nationality__in=european_countries).count()
        south_american_count = Player.objects.filter(nationality__in=south_american_countries).count()
        
        self.stdout.write(f'\n🗺️ Geographic Distribution:')
        self.stdout.write(f'  • European Players: {european_count}')
        self.stdout.write(f'  • South American Players: {south_american_count}')

    def _calculate_completeness_score(self, player) -> int:
        """Calculate data completeness score for a player"""
        fields_to_check = [
            'name', 'team', 'position', 'nationality', 'date_of_birth',
            'height', 'weight', 'photo_url', 'description'
        ]
        
        completed_fields = 0
        total_fields = len(fields_to_check)
        
        for field in fields_to_check:
            value = getattr(player, field)
            if field == 'team':
                if value is not None:
                    completed_fields += 1
            else:
                if value and str(value).strip():
                    completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)
