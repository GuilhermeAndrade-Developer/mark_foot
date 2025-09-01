from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics.services.report_service import AnalyticsDashboardService
from analytics.models import UserAnalyticsPreference, AnalyticsDashboard
from core.models import Team, Player


class Command(BaseCommand):
    help = 'Test analytics dashboard functionality'
    
    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, default=1, help='User ID for dashboard')
    
    def handle(self, *args, **options):
        user_id = options['user_id']
        
        try:
            # Get user
            user = User.objects.get(id=user_id)
            self.stdout.write(f"📊 Testing dashboard for user: {user.username}")
            
            # Create dashboard service
            dashboard_service = AnalyticsDashboardService()
            
            # Create or get default dashboard
            dashboard = dashboard_service.create_default_dashboard(user)
            self.stdout.write(f"📋 Dashboard: {dashboard.name}")
            
            # Get dashboard data
            dashboard_data = dashboard_service.get_dashboard_data(user)
            
            self.stdout.write(self.style.SUCCESS("✅ Dashboard created/updated successfully!"))
            self.stdout.write(f"🆔 Dashboard ID: {dashboard.id}")
            self.stdout.write(f"📊 Widgets count: {len(dashboard.widgets)}")
            
            # Show widget data
            data = dashboard_data['data']
            self.stdout.write("\n📈 Dashboard Data:")
            
            if 'team_form' in data:
                self.stdout.write(f"   Team Form: {len(data['team_form'])} teams")
                for team in data['team_form'][:3]:
                    form_str = ''.join(team.get('form', []))
                    self.stdout.write(f"   - {team['team_name']}: {form_str}")
            
            if 'player_stats' in data:
                self.stdout.write(f"   Player Stats: {len(data['player_stats'])} players")
                for player in data['player_stats'][:3]:
                    self.stdout.write(f"   - {player['name']} ({player['team']})")
            
            if 'match_predictions' in data:
                self.stdout.write(f"   Match Predictions: {len(data['match_predictions'])} matches")
                for match in data['match_predictions'][:3]:
                    self.stdout.write(f"   - {match['match']} on {match['date']}")
            
            if 'league_standings' in data:
                self.stdout.write(f"   League Standings: {len(data['league_standings'])} teams")
                for standing in data['league_standings'][:3]:
                    self.stdout.write(f"   - {standing['position']}. {standing['team']} ({standing['points']} pts)")
            
            # Show user preferences
            try:
                preferences = UserAnalyticsPreference.objects.get(user=user)
                self.stdout.write(f"\n⚙️ User Preferences:")
                self.stdout.write(f"   Report Frequency: {preferences.report_frequency}")
                self.stdout.write(f"   Auto Generate: {preferences.auto_generate_reports}")
                self.stdout.write(f"   Email Reports: {preferences.email_reports}")
                self.stdout.write(f"   WhatsApp Reports: {preferences.whatsapp_reports}")
                self.stdout.write(f"   Favorite Teams: {preferences.favorite_teams.count()}")
                self.stdout.write(f"   Favorite Players: {preferences.favorite_players.count()}")
            except UserAnalyticsPreference.DoesNotExist:
                self.stdout.write("\n⚙️ No user preferences found")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User with ID {user_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
