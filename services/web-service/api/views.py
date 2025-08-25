"""
API Views for Mark Foot Football Analysis System
"""
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import (
    Area, Competition, Team, Season, Match, Standing, 
    ApiSyncLog, Player, PlayerStatistics, PlayerTransfer
)
from .serializers import (
    AreaSerializer, CompetitionSerializer, TeamSerializer, 
    SeasonSerializer, MatchSerializer, StandingSerializer,
    ApiSyncLogSerializer, PlayerSerializer, PlayerStatisticsSerializer,
    PlayerTransferSerializer, DashboardStatsSerializer, 
    RecentMatchSerializer, TopPlayerSerializer
)


@extend_schema_view(
    list=extend_schema(summary="List all areas"),
    retrieve=extend_schema(summary="Get area details"),
    create=extend_schema(summary="Create new area"),
    update=extend_schema(summary="Update area"),
    destroy=extend_schema(summary="Delete area"),
)
class AreaViewSet(viewsets.ModelViewSet):
    """ViewSet for Area model"""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary="List all competitions"),
    retrieve=extend_schema(summary="Get competition details"),
)
class CompetitionViewSet(viewsets.ModelViewSet):
    """ViewSet for Competition model"""
    queryset = Competition.objects.select_related('area').all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'plan', 'area']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary="List all teams"),
    retrieve=extend_schema(summary="Get team details"),
)
class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team model"""
    queryset = Team.objects.select_related('area').all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['area', 'founded']
    search_fields = ['name', 'short_name', 'tla']
    ordering_fields = ['name', 'founded', 'created_at']
    ordering = ['name']

    @extend_schema(summary="Get team players")
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """Get all players for a specific team"""
        team = self.get_object()
        players = Player.objects.filter(team=team)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all seasons"),
    retrieve=extend_schema(summary="Get season details"),
)
class SeasonViewSet(viewsets.ModelViewSet):
    """ViewSet for Season model"""
    queryset = Season.objects.select_related('competition', 'winner_team').all()
    serializer_class = SeasonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competition', 'available']
    search_fields = ['competition__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']


@extend_schema_view(
    list=extend_schema(summary="List all matches"),
    retrieve=extend_schema(summary="Get match details"),
)
class MatchViewSet(viewsets.ModelViewSet):
    """ViewSet for Match model"""
    queryset = Match.objects.select_related(
        'competition', 'season', 'home_team', 'away_team'
    ).all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competition', 'season', 'home_team', 'away_team', 'status']
    search_fields = ['home_team__name', 'away_team__name', 'competition__name']
    ordering_fields = ['utc_date', 'created_at']
    ordering = ['-utc_date']

    @extend_schema(summary="Get recent matches")
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent matches (last 7 days)"""
        week_ago = timezone.now() - timedelta(days=7)
        recent_matches = self.queryset.filter(
            utc_date__gte=week_ago
        ).order_by('-utc_date')[:20]
        
        serializer = RecentMatchSerializer(recent_matches, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Get matches by date range")
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get matches within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "start_date and end_date parameters are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        matches = self.queryset.filter(
            utc_date__date__gte=start_date,
            utc_date__date__lte=end_date
        )
        
        page = self.paginate_queryset(matches)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all standings"),
    retrieve=extend_schema(summary="Get standing details"),
)
class StandingViewSet(viewsets.ModelViewSet):
    """ViewSet for Standing model"""
    queryset = Standing.objects.select_related(
        'competition', 'season', 'team'
    ).all()
    serializer_class = StandingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['competition', 'season', 'team', 'type', 'stage']
    search_fields = ['team__name', 'competition__name']
    ordering_fields = ['position', 'points', 'goal_difference', 'snapshot_date']
    ordering = ['position']

    @extend_schema(summary="Get current standings for a competition")
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current standings for a specific competition"""
        competition_id = request.query_params.get('competition_id')
        
        if not competition_id:
            return Response(
                {"error": "competition_id parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        latest_standings = self.queryset.filter(
            competition_id=competition_id,
            type='TOTAL'
        ).order_by('position')
        
        serializer = self.get_serializer(latest_standings, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List all players"),
    retrieve=extend_schema(summary="Get player details"),
)
class PlayerViewSet(viewsets.ModelViewSet):
    """ViewSet for Player model"""
    queryset = Player.objects.select_related('team', 'team__area').all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'nationality', 'position_category', 'status']
    search_fields = ['name', 'short_name', 'nationality']
    ordering_fields = ['name', 'age', 'created_at']
    ordering = ['name']

    @extend_schema(summary="Get player statistics")
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get all statistics for a specific player"""
        player = self.get_object()
        stats = PlayerStatistics.objects.filter(player=player)
        serializer = PlayerStatisticsSerializer(stats, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Get player transfers")
    @action(detail=True, methods=['get'])
    def transfers(self, request, pk=None):
        """Get all transfers for a specific player"""
        player = self.get_object()
        transfers = PlayerTransfer.objects.filter(player=player)
        serializer = PlayerTransferSerializer(transfers, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Get top scorers")
    @action(detail=False, methods=['get'])
    def top_scorers(self, request):
        """Get top goal scorers"""
        top_scorers = Player.objects.annotate(
            total_goals=Sum('statistics__goals'),
            total_assists=Sum('statistics__assists'),
            total_appearances=Sum('statistics__appearances')
        ).filter(
            total_goals__gt=0
        ).order_by('-total_goals')[:10]
        
        serializer_data = []
        for player in top_scorers:
            serializer_data.append({
                'player_name': player.name,
                'team_name': player.team.name if player.team else 'No Team',
                'total_goals': player.total_goals or 0,
                'total_assists': player.total_assists or 0,
                'total_appearances': player.total_appearances or 0,
            })
        
        serializer = TopPlayerSerializer(serializer_data, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="List player statistics"),
    retrieve=extend_schema(summary="Get player statistics details"),
)
class PlayerStatisticsViewSet(viewsets.ModelViewSet):
    """ViewSet for PlayerStatistics model"""
    queryset = PlayerStatistics.objects.select_related(
        'player', 'season', 'competition'
    ).all()
    serializer_class = PlayerStatisticsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['player', 'season', 'competition']
    search_fields = ['player__name']
    ordering_fields = ['goals', 'assists', 'appearances', 'rating']
    ordering = ['-goals']


@extend_schema_view(
    list=extend_schema(summary="List player transfers"),
    retrieve=extend_schema(summary="Get player transfer details"),
)
class PlayerTransferViewSet(viewsets.ModelViewSet):
    """ViewSet for PlayerTransfer model"""
    queryset = PlayerTransfer.objects.select_related(
        'player', 'from_team', 'to_team'
    ).all()
    serializer_class = PlayerTransferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['player', 'from_team', 'to_team', 'transfer_type']
    search_fields = ['player__name', 'from_team__name', 'to_team__name']
    ordering_fields = ['transfer_date', 'created_at']
    ordering = ['-transfer_date']


@extend_schema_view(
    list=extend_schema(summary="List API sync logs"),
    retrieve=extend_schema(summary="Get API sync log details"),
)
class ApiSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for ApiSyncLog model"""
    queryset = ApiSyncLog.objects.all()
    serializer_class = ApiSyncLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['endpoint', 'http_status']
    search_fields = ['endpoint']
    ordering_fields = ['sync_date', 'created_at']
    ordering = ['-sync_date']


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard statistics and data"""
    permission_classes = [AllowAny]  # Allow public access for demo

    @extend_schema(
        summary="Get dashboard statistics",
        responses={200: DashboardStatsSerializer}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get general statistics for dashboard"""
        stats = {
            'total_teams': Team.objects.count(),
            'total_players': Player.objects.count(),
            'total_competitions': Competition.objects.count(),
            'total_matches': Match.objects.count(),
            'recent_matches_count': Match.objects.filter(
                utc_date__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'active_players_count': Player.objects.filter(
                status='Active'
            ).count(),
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Get recent matches for dashboard",
        responses={200: RecentMatchSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def recent_matches(self, request):
        """Get recent matches for dashboard"""
        recent_matches = Match.objects.select_related(
            'home_team', 'away_team', 'competition'
        ).filter(
            utc_date__gte=timezone.now() - timedelta(days=30)
        ).order_by('-utc_date')[:10]
        
        serializer = RecentMatchSerializer(recent_matches, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get top scorers for dashboard",
        responses={200: TopPlayerSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def top_scorers(self, request):
        """Get top scorers for dashboard"""
        top_scorers = Player.objects.annotate(
            total_goals=Sum('statistics__goals')
        ).filter(
            total_goals__gt=0
        ).order_by('-total_goals')[:5]
        
        serializer_data = []
        for player in top_scorers:
            serializer_data.append({
                'player_name': player.name,
                'team_name': player.team.name if player.team else 'No Team',
                'total_goals': player.total_goals or 0,
                'total_assists': 0,  # Could be enhanced later
                'total_appearances': 0,  # Could be enhanced later
            })
        
        serializer = TopPlayerSerializer(serializer_data, many=True)
        return Response(serializer.data)
