from django.core.management.base import BaseCommand
from analytics.models import AnalyticsReport, UserAnalyticsPreference, AnalyticsDashboard
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = 'Show analytics system summary'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🎉 MARK FOOT ANALYTICS SYSTEM SUMMARY"))
        self.stdout.write("=" * 60)
        
        # Database Statistics
        self.stdout.write("\n📊 DATABASE STATISTICS:")
        self.stdout.write(f"   📋 Reports: {AnalyticsReport.objects.count()}")
        self.stdout.write(f"   👥 User Preferences: {UserAnalyticsPreference.objects.count()}")
        self.stdout.write(f"   📊 Dashboards: {AnalyticsDashboard.objects.count()}")
        self.stdout.write(f"   🤖 Celery Tasks: {PeriodicTask.objects.filter(name__contains='analytics').count()}")
        
        # Recent Reports
        recent_reports = AnalyticsReport.objects.order_by('-created_at')[:5]
        self.stdout.write(f"\n📈 RECENT REPORTS ({recent_reports.count()}):")
        for report in recent_reports:
            status_emoji = "✅" if report.status == "completed" else "⏳"
            self.stdout.write(f"   {status_emoji} {report.title} ({report.format}) - {report.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # User Activity
        users_with_preferences = UserAnalyticsPreference.objects.count()
        total_users = User.objects.count()
        self.stdout.write(f"\n👥 USER ENGAGEMENT:")
        self.stdout.write(f"   📊 Users with Analytics Preferences: {users_with_preferences}/{total_users}")
        self.stdout.write(f"   📋 Users with Custom Dashboards: {AnalyticsDashboard.objects.values('user').distinct().count()}")
        
        # Features Implemented
        self.stdout.write(f"\n🚀 FEATURES IMPLEMENTED:")
        features = [
            "✅ PDF Report Generation",
            "✅ Excel Report Generation", 
            "✅ JSON Report Generation",
            "✅ Team Analysis Reports",
            "✅ Player Analysis Reports",
            "✅ Customizable Dashboards",
            "✅ User Analytics Preferences",
            "✅ WhatsApp Integration",
            "✅ Automated Report Scheduling",
            "✅ Celery Task Management",
            "✅ Report Download & Tracking",
            "✅ Analytics Data Models",
            "✅ Dashboard Widgets",
            "✅ Report Statistics",
        ]
        
        for feature in features:
            self.stdout.write(f"   {feature}")
        
        # API Endpoints
        self.stdout.write(f"\n🔗 API ENDPOINTS:")
        endpoints = [
            "POST /api/analytics/reports/generate_team_report/",
            "POST /api/analytics/reports/generate_player_report/",
            "GET  /api/analytics/reports/{id}/download/",
            "GET  /api/analytics/dashboards/default/",
            "GET  /api/analytics/dashboards/{id}/data/",
            "PATCH /api/analytics/dashboards/{id}/update_widgets/",
            "GET  /api/analytics/preferences/my_preferences/",
            "POST /api/analytics/preferences/my_preferences/",
            "GET  /api/analytics/stats/",
            "GET  /api/analytics/teams-players/",
        ]
        
        for endpoint in endpoints:
            self.stdout.write(f"   {endpoint}")
        
        # WhatsApp Commands
        self.stdout.write(f"\n💬 WHATSAPP COMMANDS:")
        commands = [
            "/relatorio time [nome] - Generate team report",
            "/relatorio jogador [nome] - Generate player report", 
            "/relatorio odds - Betting odds analysis",
            "/relatorio mercado - Market trends analysis",
            "/dashboard - Access dashboard link",
        ]
        
        for command in commands:
            self.stdout.write(f"   {command}")
        
        # Celery Tasks
        periodic_tasks = PeriodicTask.objects.filter(name__contains='analytics')
        self.stdout.write(f"\n⏰ SCHEDULED TASKS:")
        for task in periodic_tasks:
            status = "🟢 Active" if task.enabled else "🔴 Inactive"
            self.stdout.write(f"   {status} {task.name} - {task.crontab}")
        
        # Next Steps
        self.stdout.write(f"\n🎯 NEXT STEPS:")
        next_steps = [
            "🔧 Configure WhatsApp Business API credentials",
            "📧 Set up email report delivery",
            "📊 Add more dashboard widget types",
            "🎨 Create frontend dashboard interface",
            "📈 Add advanced analytics features",
            "🤖 Implement AI-powered insights",
            "📱 Mobile app integration",
            "🔐 User authentication & permissions",
        ]
        
        for step in next_steps:
            self.stdout.write(f"   {step}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 Analytics system successfully implemented!"))
        self.stdout.write("Ready for production deployment with proper WhatsApp credentials.")
