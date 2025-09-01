from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import os
import json
import mimetypes

from .models import (
    UserAnalyticsPreference, AnalyticsReport, TeamAnalytics, 
    PlayerAnalytics, MatchAnalytics, AnalyticsDashboard
)
from .services.report_service import ReportGenerationService, AnalyticsDashboardService
from .tasks import generate_team_report_async, generate_player_report_async
from core.models import Team, Player


class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsReport.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def generate_team_report(self, request):
        """Generate team report asynchronously"""
        try:
            team_id = request.data.get('team_id')
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            format = request.data.get('format', 'pdf')
            
            if not all([team_id, date_from, date_to]):
                return Response({
                    'error': 'team_id, date_from, and date_to are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate team exists
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return Response({
                    'error': 'Team not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate dates
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                
                if date_from_obj > date_to_obj:
                    return Response({
                        'error': 'date_from must be before date_to'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if date_to_obj > timezone.now().date():
                    return Response({
                        'error': 'date_to cannot be in the future'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Start async task
            task = generate_team_report_async.delay(
                request.user.id, team_id, date_from, date_to, format
            )
            
            return Response({
                'message': 'Report generation started',
                'task_id': task.id,
                'team_name': team.name,
                'estimated_completion': '2-5 minutes'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_player_report(self, request):
        """Generate player report asynchronously"""
        try:
            player_id = request.data.get('player_id')
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            format = request.data.get('format', 'pdf')
            
            if not all([player_id, date_from, date_to]):
                return Response({
                    'error': 'player_id, date_from, and date_to are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate player exists
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                return Response({
                    'error': 'Player not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate dates
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                
                if date_from_obj > date_to_obj:
                    return Response({
                        'error': 'date_from must be before date_to'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Start async task
            task = generate_player_report_async.delay(
                request.user.id, player_id, date_from, date_to, format
            )
            
            return Response({
                'message': 'Report generation started',
                'task_id': task.id,
                'player_name': player.name,
                'estimated_completion': '2-5 minutes'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download generated report file"""
        try:
            report = get_object_or_404(AnalyticsReport, pk=pk, user=request.user)
            
            if report.status != 'completed':
                return Response({
                    'error': f'Report is not ready. Status: {report.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not report.file_path or not os.path.exists(report.file_path):
                return Response({
                    'error': 'Report file not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Increment download count
            report.download_count += 1
            report.save(update_fields=['download_count'])
            
            # Serve file
            with open(report.file_path, 'rb') as f:
                file_data = f.read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(report.file_path)
            if not content_type:
                if report.format == 'pdf':
                    content_type = 'application/pdf'
                elif report.format == 'excel':
                    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                else:
                    content_type = 'application/octet-stream'
            
            filename = f"{report.title.replace(' ', '_')}_{report.created_at.strftime('%Y%m%d')}.{report.format}"
            
            response = HttpResponse(file_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(file_data)
            
            return response
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyticsDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics dashboards"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsDashboard.objects.filter(user=self.request.user).order_by('-updated_at')
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get or create default dashboard for user"""
        try:
            dashboard_service = AnalyticsDashboardService()
            dashboard_data = dashboard_service.get_dashboard_data(request.user)
            
            return Response({
                'dashboard': {
                    'id': str(dashboard_data['dashboard'].id),
                    'name': dashboard_data['dashboard'].name,
                    'widgets': dashboard_data['dashboard'].widgets,
                    'layout_config': dashboard_data['dashboard'].layout_config,
                },
                'data': dashboard_data['data'],
                'last_updated': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get dashboard data"""
        try:
            dashboard = get_object_or_404(AnalyticsDashboard, pk=pk, user=request.user)
            dashboard_service = AnalyticsDashboardService()
            dashboard_data = dashboard_service.get_dashboard_data(request.user, pk)
            
            return Response({
                'data': dashboard_data['data'],
                'last_updated': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'])
    def update_widgets(self, request, pk=None):
        """Update dashboard widgets configuration"""
        try:
            dashboard = get_object_or_404(AnalyticsDashboard, pk=pk, user=request.user)
            
            widgets = request.data.get('widgets')
            layout_config = request.data.get('layout_config')
            
            if widgets is not None:
                dashboard.widgets = widgets
            
            if layout_config is not None:
                dashboard.layout_config = layout_config
            
            dashboard.save()
            
            return Response({
                'message': 'Dashboard updated successfully',
                'dashboard': {
                    'id': str(dashboard.id),
                    'name': dashboard.name,
                    'widgets': dashboard.widgets,
                    'layout_config': dashboard.layout_config,
                }
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAnalyticsPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for user analytics preferences"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAnalyticsPreference.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'post'])
    def my_preferences(self, request):
        """Get or create user preferences"""
        if request.method == 'GET':
            try:
                preferences = UserAnalyticsPreference.objects.get(user=request.user)
                return Response({
                    'id': str(preferences.id),
                    'report_frequency': preferences.report_frequency,
                    'auto_generate_reports': preferences.auto_generate_reports,
                    'email_reports': preferences.email_reports,
                    'whatsapp_reports': preferences.whatsapp_reports,
                    'enabled_widgets': preferences.enabled_widgets,
                    'favorite_teams': [{'id': team.id, 'name': team.name} for team in preferences.favorite_teams.all()],
                    'favorite_players': [{'id': player.id, 'name': player.name} for player in preferences.favorite_players.all()],
                })
            except UserAnalyticsPreference.DoesNotExist:
                # Create default preferences
                preferences = UserAnalyticsPreference.objects.create(user=request.user)
                return Response({
                    'id': str(preferences.id),
                    'report_frequency': preferences.report_frequency,
                    'auto_generate_reports': preferences.auto_generate_reports,
                    'email_reports': preferences.email_reports,
                    'whatsapp_reports': preferences.whatsapp_reports,
                    'enabled_widgets': preferences.enabled_widgets,
                    'favorite_teams': [],
                    'favorite_players': [],
                })
        
        elif request.method == 'POST':
            try:
                preferences, created = UserAnalyticsPreference.objects.get_or_create(user=request.user)
                
                # Update preferences
                if 'report_frequency' in request.data:
                    preferences.report_frequency = request.data['report_frequency']
                if 'auto_generate_reports' in request.data:
                    preferences.auto_generate_reports = request.data['auto_generate_reports']
                if 'email_reports' in request.data:
                    preferences.email_reports = request.data['email_reports']
                if 'whatsapp_reports' in request.data:
                    preferences.whatsapp_reports = request.data['whatsapp_reports']
                if 'enabled_widgets' in request.data:
                    preferences.enabled_widgets = request.data['enabled_widgets']
                
                preferences.save()
                
                # Update favorite teams
                if 'favorite_teams' in request.data:
                    team_ids = request.data['favorite_teams']
                    teams = Team.objects.filter(id__in=team_ids)
                    preferences.favorite_teams.set(teams)
                
                # Update favorite players
                if 'favorite_players' in request.data:
                    player_ids = request.data['favorite_players']
                    players = Player.objects.filter(id__in=player_ids)
                    preferences.favorite_players.set(players)
                
                return Response({
                    'message': 'Preferences updated successfully',
                    'preferences': {
                        'id': str(preferences.id),
                        'report_frequency': preferences.report_frequency,
                        'auto_generate_reports': preferences.auto_generate_reports,
                        'email_reports': preferences.email_reports,
                        'whatsapp_reports': preferences.whatsapp_reports,
                        'enabled_widgets': preferences.enabled_widgets,
                    }
                })
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_stats(request):
    """Get analytics statistics for user"""
    try:
        user = request.user
        
        # Count user's reports
        total_reports = AnalyticsReport.objects.filter(user=user).count()
        completed_reports = AnalyticsReport.objects.filter(user=user, status='completed').count()
        pending_reports = AnalyticsReport.objects.filter(user=user, status__in=['pending', 'generating']).count()
        
        # Get recent reports
        recent_reports = AnalyticsReport.objects.filter(user=user).order_by('-created_at')[:5]
        recent_reports_data = []
        for report in recent_reports:
            recent_reports_data.append({
                'id': str(report.id),
                'title': report.title,
                'report_type': report.report_type,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'generation_time': report.generation_time,
            })
        
        # Check if user has preferences
        has_preferences = UserAnalyticsPreference.objects.filter(user=user).exists()
        
        # Check if user has dashboards
        dashboards_count = AnalyticsDashboard.objects.filter(user=user).count()
        
        return Response({
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'pending_reports': pending_reports,
            'recent_reports': recent_reports_data,
            'has_preferences': has_preferences,
            'dashboards_count': dashboards_count,
            'features': {
                'team_reports': True,
                'player_reports': True,
                'custom_dashboards': True,
                'whatsapp_integration': True,
                'automated_reports': True,
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_teams_and_players(request):
    """Get available teams and players for reports"""
    try:
        # Get teams with recent matches
        teams = Team.objects.all().order_by('name')[:50]  # Limit for performance
        teams_data = []
        for team in teams:
            teams_data.append({
                'id': team.id,
                'name': team.name,
                'venue': team.venue,
                'founded': team.founded,
            })
        
        # Get players with teams
        players = Player.objects.filter(team__isnull=False).order_by('name')[:100]  # Limit for performance
        players_data = []
        for player in players:
            players_data.append({
                'id': player.id,
                'name': player.name,
                'position': player.position,
                'team': player.team.name if player.team else None,
                'nationality': player.nationality,
            })
        
        return Response({
            'teams': teams_data,
            'players': players_data,
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
