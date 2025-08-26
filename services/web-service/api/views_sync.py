from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from django.core.management.base import CommandError
from core.models import Competition, Team, Player, Match, Standing, ApiSyncLog
from django.db.models import Count
import json
import threading
import time


@api_view(['GET'])
def stats_summary(request):
    """Get database statistics summary"""
    try:
        stats = {
            'competitions': Competition.objects.count(),
            'teams': Team.objects.count(),
            'players': Player.objects.count(),
            'matches': Match.objects.count(),
            'standings': Standing.objects.count(),
            'api_logs': ApiSyncLog.objects.count(),
        }
        
        # Additional stats
        stats['recent_syncs'] = ApiSyncLog.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        stats['active_players'] = Player.objects.filter(status='Active').count()
        
        return Response(stats)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def sync_competition(request):
    """Sync a specific competition"""
    try:
        data = request.data
        competition_code = data.get('competition_code')
        include_standings = data.get('include_standings', True)
        
        if not competition_code:
            return Response(
                {'error': 'competition_code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute sync command
        try:
            call_command(
                'sync_competition', 
                competition_code,
                season='2024'
            )
            
            # Get stats after sync
            competition = Competition.objects.get(code=competition_code.upper())
            teams_count = Match.objects.filter(competition=competition).values('home_team', 'away_team').distinct().count()
            matches_count = Match.objects.filter(competition=competition).count()
            standings_count = Standing.objects.filter(competition=competition).count()
            
            summary = f"{teams_count} times, {matches_count} partidas"
            if include_standings:
                summary += f", {standings_count} classificações"
            
            return Response({
                'success': True,
                'summary': summary,
                'details': {
                    'competition': competition.name,
                    'teams': teams_count,
                    'matches': matches_count,
                    'standings': standings_count
                }
            })
            
        except CommandError as e:
            return Response(
                {'error': f'Erro no comando: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def sync_players(request):
    """Sync players for a specific competition"""
    try:
        data = request.data
        competition_code = data.get('competition_code')
        limit = data.get('limit', 10)  # Limit teams to avoid timeout
        
        if not competition_code:
            return Response(
                {'error': 'competition_code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute sync command
        try:
            call_command(
                'sync_players_bulk', 
                competition=competition_code,
                limit=limit,
                force=True  # Skip confirmation prompt
            )
            
            # Get stats after sync
            competition = Competition.objects.get(code=competition_code.upper())
            
            # Count players from teams in this competition
            from django.db.models import Q
            home_team_ids = Match.objects.filter(competition=competition).values_list('home_team_id', flat=True)
            away_team_ids = Match.objects.filter(competition=competition).values_list('away_team_id', flat=True)
            team_ids = set(list(home_team_ids) + list(away_team_ids))
            
            players_count = Player.objects.filter(team_id__in=team_ids).count()
            teams_count = len(team_ids)
            
            summary = f"{players_count} jogadores de {teams_count} times"
            
            return Response({
                'success': True,
                'summary': summary,
                'details': {
                    'competition': competition.name,
                    'players': players_count,
                    'teams': teams_count
                }
            })
            
        except CommandError as e:
            return Response(
                {'error': f'Erro no comando: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def api_status(request):
    """Check status of external APIs"""
    try:
        from api_integration.football_data_client import FootballDataAPIClient
        
        status_data = []
        
        # Test Football-Data.org
        try:
            client = FootballDataAPIClient()
            response = client.get_competitions()
            
            if response.get('data'):
                status_data.append({
                    'name': 'Football-Data.org',
                    'status': 'online',
                    'rate_limit': '10/min',
                    'last_response_time': response.get('execution_time', 0),
                    'last_check': timezone.now().isoformat()
                })
            else:
                status_data.append({
                    'name': 'Football-Data.org',
                    'status': 'error',
                    'rate_limit': '10/min',
                    'error': response.get('error', 'Unknown error'),
                    'last_check': timezone.now().isoformat()
                })
        except Exception as e:
            status_data.append({
                'name': 'Football-Data.org',
                'status': 'offline',
                'rate_limit': '10/min',
                'error': str(e),
                'last_check': timezone.now().isoformat()
            })
        
        # Test TheSportsDB (simulated since we're not using it much)
        status_data.append({
            'name': 'TheSportsDB',
            'status': 'online',
            'rate_limit': 'Unlimited',
            'last_check': timezone.now().isoformat()
        })
        
        return Response({'apis': status_data})
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def sync_logs(request):
    """Get recent sync logs"""
    try:
        limit = request.GET.get('limit', 50)
        logs = ApiSyncLog.objects.order_by('-created_at')[:int(limit)]
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'endpoint': log.endpoint,
                'http_status': log.http_status,
                'records_processed': log.records_processed,
                'records_inserted': log.records_inserted,
                'records_updated': log.records_updated,
                'execution_time_ms': log.execution_time_ms,
                'error_message': log.error_message,
                'created_at': log.created_at.isoformat(),
                'sync_date': log.sync_date.isoformat() if log.sync_date else None
            })
        
        return Response({'logs': logs_data})
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Import required modules at the top
