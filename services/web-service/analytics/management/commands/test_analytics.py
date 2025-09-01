from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from analytics.services.report_service import ReportGenerationService
from core.models import Team


class Command(BaseCommand):
    help = 'Test analytics report generation'
    
    def add_arguments(self, parser):
        parser.add_argument('--team-id', type=int, help='Team ID for report')
        parser.add_argument('--user-id', type=int, help='User ID for report')
        parser.add_argument('--format', type=str, default='pdf', help='Report format (pdf, excel, json)')
    
    def handle(self, *args, **options):
        team_id = options.get('team_id', 1903)  # Default to Corinthians
        user_id = options.get('user_id', 1)  # Default to first user
        format = options.get('format', 'pdf')
        
        try:
            # Get user
            user = User.objects.get(id=user_id)
            self.stdout.write(f"📊 Testing report generation for user: {user.username}")
            
            # Get team
            team = Team.objects.get(id=team_id)
            self.stdout.write(f"⚽ Team: {team.name}")
            
            # Set date range (last 30 days)
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=30)
            
            self.stdout.write(f"📅 Date range: {date_from} to {date_to}")
            self.stdout.write(f"📄 Format: {format}")
            
            # Generate report
            self.stdout.write("🔄 Generating report...")
            service = ReportGenerationService()
            report = service.generate_team_report(user, team_id, date_from, date_to, format)
            
            self.stdout.write(self.style.SUCCESS(f"✅ Report generated successfully!"))
            self.stdout.write(f"📋 Report ID: {report.id}")
            self.stdout.write(f"📁 File path: {report.file_path}")
            self.stdout.write(f"⏱️ Generation time: {report.generation_time:.2f}s")
            self.stdout.write(f"📊 File size: {report.file_size} bytes")
            self.stdout.write(f"📈 Status: {report.status}")
            
            # Show some report data
            if report.content_data:
                stats = report.content_data.get('statistics', {})
                self.stdout.write("\n📈 Quick Stats:")
                self.stdout.write(f"   Matches: {stats.get('total_matches', 0)}")
                self.stdout.write(f"   Wins: {stats.get('wins', 0)}")
                self.stdout.write(f"   Goals For: {stats.get('goals_for', 0)}")
                self.stdout.write(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User with ID {user_id} not found"))
        except Team.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Team with ID {team_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
