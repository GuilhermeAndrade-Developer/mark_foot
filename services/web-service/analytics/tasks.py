from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from .services.report_service import ReportGenerationService, AnalyticsDashboardService
from whatsapp_integration.services import WhatsAppService


@shared_task
def generate_team_report_async(user_id, team_id, date_from, date_to, format='pdf'):
    """Generate team report asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        service = ReportGenerationService()
        
        # Convert string dates to date objects
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report = service.generate_team_report(user, team_id, date_from, date_to, format)
        
        # Send WhatsApp notification if user has WhatsApp integration
        try:
            whatsapp_service = WhatsAppService()
            message = f"""📊 {report.title}
📅 Período: {report.date_from.strftime('%d/%m')} a {report.date_to.strftime('%d/%m')}
⏱️ Gerado em {report.generation_time:.1f}s

🔗 Baixar PDF: {settings.FRONTEND_URL}/reports/{report.id}/pdf
📱 Ver no dashboard: {settings.FRONTEND_URL}/dashboard

📈 Dados inclusos:
✅ Performance geral
✅ Forma recente
✅ Estatísticas detalhadas
✅ Histórico de jogos"""
            
            whatsapp_service.send_message(user, message)
        except Exception as e:
            print(f"Failed to send WhatsApp notification: {e}")
        
        return {
            'status': 'completed',
            'report_id': str(report.id),
            'file_path': report.file_path,
            'generation_time': report.generation_time
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def generate_player_report_async(user_id, player_id, date_from, date_to, format='pdf'):
    """Generate player report asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        service = ReportGenerationService()
        
        # Convert string dates to date objects
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        report = service.generate_player_report(user, player_id, date_from, date_to, format)
        
        # Send WhatsApp notification if user has WhatsApp integration
        try:
            whatsapp_service = WhatsAppService()
            message = f"""📊 {report.title}
📅 Período: {report.date_from.strftime('%d/%m')} a {report.date_to.strftime('%d/%m')}

🔗 Baixar PDF: {settings.FRONTEND_URL}/reports/{report.id}/pdf

📈 Análise incluída:
✅ Estatísticas de performance
✅ Métricas avançadas
✅ Comparação com média
✅ Evolução temporal"""
            
            whatsapp_service.send_message(user, message)
        except Exception as e:
            print(f"Failed to send WhatsApp notification: {e}")
        
        return {
            'status': 'completed',
            'report_id': str(report.id),
            'file_path': report.file_path,
            'generation_time': report.generation_time
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def send_weekly_reports():
    """Send weekly reports to subscribed users"""
    from .models import UserAnalyticsPreference
    
    users_for_weekly = UserAnalyticsPreference.objects.filter(
        report_frequency='weekly',
        auto_generate_reports=True
    )
    
    date_to = timezone.now().date()
    date_from = date_to - timedelta(days=7)
    
    reports_generated = 0
    
    for preference in users_for_weekly:
        user = preference.user
        
        # Generate reports for favorite teams
        for team in preference.favorite_teams.all()[:3]:  # Limit to 3 teams
            try:
                generate_team_report_async.delay(
                    user.id, team.id, date_from.strftime('%Y-%m-%d'), 
                    date_to.strftime('%Y-%m-%d'), 'pdf'
                )
                reports_generated += 1
            except Exception as e:
                print(f"Failed to generate weekly report for user {user.id}, team {team.id}: {e}")
        
        # Send WhatsApp summary if enabled
        if preference.whatsapp_reports:
            try:
                whatsapp_service = WhatsAppService()
                message = f"""📊 Relatórios Semanais Mark Foot

Seus relatórios estão sendo gerados:
"""
                for team in preference.favorite_teams.all()[:3]:
                    message += f"📈 {team.name}\n"
                
                message += f"""
⏳ Você receberá os links em alguns minutos!
📱 Acesse também: {settings.FRONTEND_URL}/dashboard"""
                
                whatsapp_service.send_message(user, message)
            except Exception as e:
                print(f"Failed to send weekly summary to user {user.id}: {e}")
    
    return {
        'status': 'completed',
        'reports_generated': reports_generated,
        'users_processed': users_for_weekly.count()
    }


@shared_task
def send_monthly_reports():
    """Send monthly reports to subscribed users"""
    from .models import UserAnalyticsPreference
    
    users_for_monthly = UserAnalyticsPreference.objects.filter(
        report_frequency='monthly',
        auto_generate_reports=True
    )
    
    date_to = timezone.now().date()
    date_from = date_to - timedelta(days=30)
    
    reports_generated = 0
    
    for preference in users_for_monthly:
        user = preference.user
        
        # Generate comprehensive monthly reports
        for team in preference.favorite_teams.all()[:5]:  # More teams for monthly
            try:
                generate_team_report_async.delay(
                    user.id, team.id, date_from.strftime('%Y-%m-%d'), 
                    date_to.strftime('%Y-%m-%d'), 'pdf'
                )
                reports_generated += 1
            except Exception as e:
                print(f"Failed to generate monthly report for user {user.id}, team {team.id}: {e}")
        
        # Generate player reports for favorite players
        for player in preference.favorite_players.all()[:3]:
            try:
                generate_player_report_async.delay(
                    user.id, player.id, date_from.strftime('%Y-%m-%d'), 
                    date_to.strftime('%Y-%m-%d'), 'pdf'
                )
                reports_generated += 1
            except Exception as e:
                print(f"Failed to generate monthly player report for user {user.id}, player {player.id}: {e}")
    
    return {
        'status': 'completed',
        'reports_generated': reports_generated,
        'users_processed': users_for_monthly.count()
    }


@shared_task
def cleanup_old_reports():
    """Clean up old report files to save storage space"""
    from .models import AnalyticsReport
    import os
    
    # Delete reports older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    old_reports = AnalyticsReport.objects.filter(
        created_at__lt=cutoff_date,
        status='completed'
    )
    
    deleted_files = 0
    deleted_records = 0
    
    for report in old_reports:
        # Delete physical file
        if report.file_path and os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
                deleted_files += 1
            except Exception as e:
                print(f"Failed to delete file {report.file_path}: {e}")
        
        # Delete database record
        report.delete()
        deleted_records += 1
    
    return {
        'status': 'completed',
        'deleted_files': deleted_files,
        'deleted_records': deleted_records
    }


@shared_task
def generate_analytics_summary(user_id):
    """Generate analytics summary for dashboard"""
    try:
        user = User.objects.get(id=user_id)
        dashboard_service = AnalyticsDashboardService()
        
        # Ensure user has default dashboard
        dashboard = dashboard_service.create_default_dashboard(user)
        
        # Get dashboard data
        dashboard_data = dashboard_service.get_dashboard_data(user)
        
        return {
            'status': 'completed',
            'dashboard_id': str(dashboard.id),
            'widgets_count': len(dashboard.widgets),
            'data_updated': timezone.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }
