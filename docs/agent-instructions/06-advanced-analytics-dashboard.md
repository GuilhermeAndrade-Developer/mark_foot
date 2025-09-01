# Advanced Analytics Dashboard and Reporting System

## Objective
Create comprehensive analytics dashboard with PDF reports, advanced statistics, data visualization, and business intelligence features for Mark Foot platform.

## Current Project Context
- Django backend with extensive match and player data
- WhatsApp integration with premium subscriptions
- Live match monitoring system
- AI analytics services for predictions
- Vue.js frontend foundation

## Technical Requirements

### 1. Analytics Data Models

#### analytics/models.py
```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Team, Player, Match, Competition

class UserAnalyticsPreference(models.Model):
    REPORT_FREQUENCY = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
    ]
    
    CHART_TYPES = [
        ('line', 'Linha'),
        ('bar', 'Barra'),
        ('pie', 'Pizza'),
        ('scatter', 'Dispersão'),
        ('radar', 'Radar'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_teams = models.ManyToManyField(Team, blank=True)
    favorite_players = models.ManyToManyField(Player, blank=True)
    favorite_competitions = models.ManyToManyField(Competition, blank=True)
    
    # Report preferences
    auto_reports = models.BooleanField(default=True)
    report_frequency = models.CharField(max_length=20, choices=REPORT_FREQUENCY, default='weekly')
    include_predictions = models.BooleanField(default=True)
    include_odds_analysis = models.BooleanField(default=True)
    include_player_stats = models.BooleanField(default=True)
    
    # Visualization preferences
    preferred_chart_type = models.CharField(max_length=20, choices=CHART_TYPES, default='line')
    dark_mode_reports = models.BooleanField(default=False)
    
    # Notification preferences
    whatsapp_reports = models.BooleanField(default=True)
    email_reports = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AnalyticsReport(models.Model):
    REPORT_TYPES = [
        ('team_performance', 'Performance de Time'),
        ('player_analysis', 'Análise de Jogador'),
        ('match_prediction', 'Previsão de Partida'),
        ('odds_analysis', 'Análise de Odds'),
        ('market_trends', 'Tendências de Mercado'),
        ('custom', 'Personalizado'),
    ]
    
    REPORT_STATUS = [
        ('generating', 'Gerando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Report parameters
    parameters = models.JSONField(default=dict)
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Report files
    pdf_file = models.FileField(upload_to='reports/pdf/', null=True, blank=True)
    excel_file = models.FileField(upload_to='reports/excel/', null=True, blank=True)
    
    # Report data
    data = models.JSONField(default=dict)
    charts_data = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='generating')
    error_message = models.TextField(blank=True)
    
    # Metrics
    generation_time = models.FloatField(null=True, blank=True)  # In seconds
    file_size = models.IntegerField(null=True, blank=True)  # In bytes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class TeamAnalytics(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Performance metrics
    matches_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    
    # Advanced metrics
    win_percentage = models.FloatField(default=0.0)
    goals_per_match = models.FloatField(default=0.0)
    goals_conceded_per_match = models.FloatField(default=0.0)
    clean_sheets = models.IntegerField(default=0)
    clean_sheet_percentage = models.FloatField(default=0.0)
    
    # Form metrics (last 5 matches)
    recent_form_points = models.IntegerField(default=0)
    recent_form_wins = models.IntegerField(default=0)
    recent_form_goals = models.IntegerField(default=0)
    
    # Home/Away split
    home_wins = models.IntegerField(default=0)
    home_draws = models.IntegerField(default=0)
    home_losses = models.IntegerField(default=0)
    away_wins = models.IntegerField(default=0)
    away_draws = models.IntegerField(default=0)
    away_losses = models.IntegerField(default=0)
    
    # Possession and shots
    avg_possession = models.FloatField(default=0.0)
    avg_shots_per_match = models.FloatField(default=0.0)
    avg_shots_on_target = models.FloatField(default=0.0)
    shot_accuracy = models.FloatField(default=0.0)
    
    # Discipline
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    
    # Market value and transfers
    estimated_market_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    transfer_activity_score = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['team', 'date']
        ordering = ['-date']

class PlayerAnalytics(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Basic stats
    matches_played = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    
    # Performance metrics
    goals_per_match = models.FloatField(default=0.0)
    assists_per_match = models.FloatField(default=0.0)
    minutes_per_goal = models.FloatField(null=True, blank=True)
    minutes_per_assist = models.FloatField(null=True, blank=True)
    
    # Advanced metrics
    expected_goals = models.FloatField(default=0.0)
    expected_assists = models.FloatField(default=0.0)
    shots_per_match = models.FloatField(default=0.0)
    shot_accuracy = models.FloatField(default=0.0)
    pass_accuracy = models.FloatField(default=0.0)
    key_passes_per_match = models.FloatField(default=0.0)
    
    # Defensive metrics (for all players)
    tackles_per_match = models.FloatField(default=0.0)
    interceptions_per_match = models.FloatField(default=0.0)
    clearances_per_match = models.FloatField(default=0.0)
    
    # Form and consistency
    form_score = models.FloatField(default=0.0)  # Performance trend
    consistency_score = models.FloatField(default=0.0)  # Performance variance
    
    # Market value
    estimated_market_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    market_value_change = models.FloatField(default=0.0)  # Percentage change
    
    class Meta:
        unique_together = ['player', 'date']
        ordering = ['-date']

class MatchAnalytics(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    
    # Pre-match analytics
    predicted_outcome = models.CharField(max_length=20, blank=True)
    prediction_confidence = models.FloatField(null=True, blank=True)
    
    # Betting analytics
    opening_odds_home = models.FloatField(null=True, blank=True)
    opening_odds_draw = models.FloatField(null=True, blank=True)
    opening_odds_away = models.FloatField(null=True, blank=True)
    closing_odds_home = models.FloatField(null=True, blank=True)
    closing_odds_draw = models.FloatField(null=True, blank=True)
    closing_odds_away = models.FloatField(null=True, blank=True)
    
    # Odds movement
    odds_movement_home = models.FloatField(default=0.0)
    odds_movement_draw = models.FloatField(default=0.0)
    odds_movement_away = models.FloatField(default=0.0)
    
    # Match metrics
    total_shots = models.IntegerField(null=True, blank=True)
    total_corners = models.IntegerField(null=True, blank=True)
    total_fouls = models.IntegerField(null=True, blank=True)
    total_cards = models.IntegerField(null=True, blank=True)
    
    # Entertainment value
    entertainment_score = models.FloatField(default=0.0)
    goal_expectation_difference = models.FloatField(default=0.0)
    
    # Post-match analysis
    prediction_accuracy = models.BooleanField(null=True, blank=True)
    value_bet_outcome = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AnalyticsDashboard(models.Model):
    WIDGET_TYPES = [
        ('team_form', 'Forma do Time'),
        ('player_stats', 'Estatísticas do Jogador'),
        ('match_predictions', 'Previsões de Partidas'),
        ('odds_tracker', 'Rastreador de Odds'),
        ('value_bets', 'Apostas de Valor'),
        ('market_trends', 'Tendências de Mercado'),
        ('competition_table', 'Tabela da Competição'),
        ('top_scorers', 'Artilheiros'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Layout configuration
    layout = models.JSONField(default=dict)  # Store widget positions and sizes
    widgets = models.JSONField(default=list)  # Store widget configurations
    
    # Dashboard settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=300)  # Seconds
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
```

### 2. Report Generation Service

#### analytics/services/report_service.py
```python
import io
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ..models import AnalyticsReport, TeamAnalytics, PlayerAnalytics, MatchAnalytics

class ReportGenerationService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for reports"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
    
    def generate_team_performance_report(self, user, team_id, date_from, date_to):
        """Generate comprehensive team performance report"""
        from core.models import Team
        
        try:
            team = Team.objects.get(id=team_id)
            
            # Create report record
            report = AnalyticsReport.objects.create(
                user=user,
                report_type='team_performance',
                title=f'Relatório de Performance - {team.name}',
                description=f'Análise completa de {date_from} a {date_to}',
                date_from=date_from,
                date_to=date_to,
                parameters={'team_id': team_id}
            )
            
            start_time = timezone.now()
            
            # Collect data
            analytics_data = self._collect_team_analytics_data(team, date_from, date_to)
            
            # Generate PDF
            pdf_buffer = self._create_team_performance_pdf(team, analytics_data, date_from, date_to)
            
            # Generate Excel
            excel_buffer = self._create_team_performance_excel(team, analytics_data, date_from, date_to)
            
            # Save files
            pdf_filename = f'team_performance_{team.id}_{date_from}_{date_to}.pdf'
            excel_filename = f'team_performance_{team.id}_{date_from}_{date_to}.xlsx'
            
            report.pdf_file.save(pdf_filename, ContentFile(pdf_buffer.getvalue()))
            report.excel_file.save(excel_filename, ContentFile(excel_buffer.getvalue()))
            
            # Update report
            generation_time = (timezone.now() - start_time).total_seconds()
            report.status = 'completed'
            report.data = analytics_data
            report.generation_time = generation_time
            report.file_size = len(pdf_buffer.getvalue())
            report.save()
            
            return report
            
        except Exception as e:
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            raise e
    
    def _collect_team_analytics_data(self, team, date_from, date_to):
        """Collect comprehensive team analytics data"""
        from core.models import Match
        
        # Get matches in date range
        matches = Match.objects.filter(
            date__date__range=[date_from, date_to]
        ).filter(
            models.Q(home_team=team) | models.Q(away_team=team)
        ).order_by('date')
        
        # Basic statistics
        total_matches = matches.count()
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        home_matches = 0
        away_matches = 0
        
        match_details = []
        
        for match in matches:
            is_home = match.home_team == team
            if is_home:
                home_matches += 1
                team_goals = match.home_score or 0
                opponent_goals = match.away_score or 0
                opponent = match.away_team
            else:
                away_matches += 1
                team_goals = match.away_score or 0
                opponent_goals = match.home_score or 0
                opponent = match.home_team
            
            goals_for += team_goals
            goals_against += opponent_goals
            
            # Determine result
            if team_goals > opponent_goals:
                wins += 1
                result = 'Vitória'
            elif team_goals < opponent_goals:
                losses += 1
                result = 'Derrota'
            else:
                draws += 1
                result = 'Empate'
            
            match_details.append({
                'date': match.date.strftime('%d/%m/%Y'),
                'opponent': opponent.name,
                'venue': 'Casa' if is_home else 'Fora',
                'score': f'{team_goals} x {opponent_goals}',
                'result': result,
                'competition': match.competition.name
            })
        
        # Calculate metrics
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        goals_per_match = goals_for / total_matches if total_matches > 0 else 0
        goals_conceded_per_match = goals_against / total_matches if total_matches > 0 else 0
        goal_difference = goals_for - goals_against
        
        # Recent form (last 5 matches)
        recent_matches = matches.order_by('-date')[:5]
        recent_form = []
        recent_points = 0
        
        for match in recent_matches:
            is_home = match.home_team == team
            team_goals = (match.home_score or 0) if is_home else (match.away_score or 0)
            opponent_goals = (match.away_score or 0) if is_home else (match.home_score or 0)
            
            if team_goals > opponent_goals:
                recent_form.append('V')
                recent_points += 3
            elif team_goals < opponent_goals:
                recent_form.append('D')
            else:
                recent_form.append('E')
                recent_points += 1
        
        # Get latest team analytics
        latest_analytics = TeamAnalytics.objects.filter(
            team=team,
            date__range=[date_from, date_to]
        ).order_by('-date').first()
        
        return {
            'team_info': {
                'name': team.name,
                'logo': team.logo.url if team.logo else None,
                'country': team.country,
            },
            'period': {
                'from': date_from.strftime('%d/%m/%Y'),
                'to': date_to.strftime('%d/%m/%Y'),
                'days': (date_to - date_from).days + 1
            },
            'summary': {
                'total_matches': total_matches,
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'win_rate': round(win_rate, 1),
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goal_difference,
                'goals_per_match': round(goals_per_match, 2),
                'goals_conceded_per_match': round(goals_conceded_per_match, 2),
                'home_matches': home_matches,
                'away_matches': away_matches
            },
            'recent_form': {
                'form': ''.join(reversed(recent_form)),
                'points': recent_points,
                'matches': len(recent_form)
            },
            'matches': match_details,
            'advanced_metrics': {
                'avg_possession': latest_analytics.avg_possession if latest_analytics else 0,
                'avg_shots': latest_analytics.avg_shots_per_match if latest_analytics else 0,
                'shot_accuracy': latest_analytics.shot_accuracy if latest_analytics else 0,
                'clean_sheets': latest_analytics.clean_sheets if latest_analytics else 0,
                'yellow_cards': latest_analytics.yellow_cards if latest_analytics else 0,
                'red_cards': latest_analytics.red_cards if latest_analytics else 0,
            }
        }
    
    def _create_team_performance_pdf(self, team, data, date_from, date_to):
        """Create PDF report for team performance"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"Relatório de Performance - {team.name}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Period
        period_text = f"Período: {data['period']['from']} a {data['period']['to']} ({data['period']['days']} dias)"
        period = Paragraph(period_text, self.body_style)
        story.append(period)
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        story.append(Paragraph("Resumo Estatístico", self.heading_style))
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Jogos', str(data['summary']['total_matches'])],
            ['Vitórias', str(data['summary']['wins'])],
            ['Empates', str(data['summary']['draws'])],
            ['Derrotas', str(data['summary']['losses'])],
            ['Taxa de Vitórias', f"{data['summary']['win_rate']}%"],
            ['Gols Marcados', str(data['summary']['goals_for'])],
            ['Gols Sofridos', str(data['summary']['goals_against'])],
            ['Saldo de Gols', str(data['summary']['goal_difference'])],
            ['Gols por Jogo', str(data['summary']['goals_per_match'])],
            ['Gols Sofridos por Jogo', str(data['summary']['goals_conceded_per_match'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Recent Form
        story.append(Paragraph("Forma Recente", self.heading_style))
        form_text = f"Últimos {data['recent_form']['matches']} jogos: {data['recent_form']['form']} ({data['recent_form']['points']} pontos)"
        story.append(Paragraph(form_text, self.body_style))
        story.append(Spacer(1, 20))
        
        # Match Details
        story.append(Paragraph("Detalhes dos Jogos", self.heading_style))
        
        match_data = [['Data', 'Adversário', 'Local', 'Resultado', 'Competição']]
        for match in data['matches'][:10]:  # Show last 10 matches
            match_data.append([
                match['date'],
                match['opponent'],
                match['venue'],
                match['score'],
                match['competition']
            ])
        
        match_table = Table(match_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1.5*inch])
        match_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(match_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_team_performance_excel(self, team, data, date_from, date_to):
        """Create Excel report for team performance"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([
                ['Jogos', data['summary']['total_matches']],
                ['Vitórias', data['summary']['wins']],
                ['Empates', data['summary']['draws']],
                ['Derrotas', data['summary']['losses']],
                ['Taxa de Vitórias (%)', data['summary']['win_rate']],
                ['Gols Marcados', data['summary']['goals_for']],
                ['Gols Sofridos', data['summary']['goals_against']],
                ['Saldo de Gols', data['summary']['goal_difference']],
            ], columns=['Métrica', 'Valor'])
            
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Matches sheet
            matches_df = pd.DataFrame(data['matches'])
            matches_df.to_excel(writer, sheet_name='Jogos', index=False)
            
            # Charts data sheet
            charts_data = {
                'Resultados': [data['summary']['wins'], data['summary']['draws'], data['summary']['losses']],
                'Labels': ['Vitórias', 'Empates', 'Derrotas']
            }
            charts_df = pd.DataFrame(charts_data)
            charts_df.to_excel(writer, sheet_name='Dados_Gráficos', index=False)
        
        buffer.seek(0)
        return buffer
    
    def generate_player_analysis_report(self, user, player_id, date_from, date_to):
        """Generate comprehensive player analysis report"""
        from core.models import Player
        
        try:
            player = Player.objects.get(id=player_id)
            
            report = AnalyticsReport.objects.create(
                user=user,
                report_type='player_analysis',
                title=f'Análise de Jogador - {player.name}',
                description=f'Relatório completo de {date_from} a {date_to}',
                date_from=date_from,
                date_to=date_to,
                parameters={'player_id': player_id}
            )
            
            start_time = timezone.now()
            
            # Collect player data
            analytics_data = self._collect_player_analytics_data(player, date_from, date_to)
            
            # Generate PDF
            pdf_buffer = self._create_player_analysis_pdf(player, analytics_data, date_from, date_to)
            
            # Save files
            pdf_filename = f'player_analysis_{player.id}_{date_from}_{date_to}.pdf'
            report.pdf_file.save(pdf_filename, ContentFile(pdf_buffer.getvalue()))
            
            # Update report
            generation_time = (timezone.now() - start_time).total_seconds()
            report.status = 'completed'
            report.data = analytics_data
            report.generation_time = generation_time
            report.file_size = len(pdf_buffer.getvalue())
            report.save()
            
            return report
            
        except Exception as e:
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            raise e
    
    def _collect_player_analytics_data(self, player, date_from, date_to):
        """Collect comprehensive player analytics data"""
        # Get player statistics from database
        player_analytics = PlayerAnalytics.objects.filter(
            player=player,
            date__range=[date_from, date_to]
        ).order_by('-date')
        
        if not player_analytics.exists():
            # Generate basic stats if no analytics data
            return self._generate_basic_player_stats(player, date_from, date_to)
        
        latest = player_analytics.first()
        
        return {
            'player_info': {
                'name': player.name,
                'position': player.position,
                'team': player.current_team.name if player.current_team else 'Sem time',
                'nationality': player.nationality,
                'age': player.age,
                'photo': player.photo.url if player.photo else None,
            },
            'period': {
                'from': date_from.strftime('%d/%m/%Y'),
                'to': date_to.strftime('%d/%m/%Y'),
            },
            'performance': {
                'matches_played': latest.matches_played,
                'minutes_played': latest.minutes_played,
                'goals': latest.goals,
                'assists': latest.assists,
                'yellow_cards': latest.yellow_cards,
                'red_cards': latest.red_cards,
                'goals_per_match': latest.goals_per_match,
                'assists_per_match': latest.assists_per_match,
                'minutes_per_goal': latest.minutes_per_goal,
                'minutes_per_assist': latest.minutes_per_assist,
            },
            'advanced_stats': {
                'expected_goals': latest.expected_goals,
                'expected_assists': latest.expected_assists,
                'shots_per_match': latest.shots_per_match,
                'shot_accuracy': latest.shot_accuracy,
                'pass_accuracy': latest.pass_accuracy,
                'key_passes_per_match': latest.key_passes_per_match,
                'tackles_per_match': latest.tackles_per_match,
                'interceptions_per_match': latest.interceptions_per_match,
            },
            'market_info': {
                'current_value': latest.estimated_market_value,
                'value_change': latest.market_value_change,
                'form_score': latest.form_score,
                'consistency_score': latest.consistency_score,
            }
        }
    
    def _generate_basic_player_stats(self, player, date_from, date_to):
        """Generate basic player stats when no analytics data available"""
        return {
            'player_info': {
                'name': player.name,
                'position': player.position,
                'team': player.current_team.name if player.current_team else 'Sem time',
                'nationality': player.nationality,
                'age': player.age,
            },
            'period': {
                'from': date_from.strftime('%d/%m/%Y'),
                'to': date_to.strftime('%d/%m/%Y'),
            },
            'performance': {
                'matches_played': 0,
                'minutes_played': 0,
                'goals': 0,
                'assists': 0,
                'note': 'Dados não disponíveis para o período selecionado'
            }
        }
    
    def _create_player_analysis_pdf(self, player, data, date_from, date_to):
        """Create PDF report for player analysis"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"Análise de Jogador - {player.name}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Player info
        if 'note' not in data['performance']:
            # Performance table
            perf_data = [
                ['Métrica', 'Valor'],
                ['Jogos', str(data['performance']['matches_played'])],
                ['Minutos', str(data['performance']['minutes_played'])],
                ['Gols', str(data['performance']['goals'])],
                ['Assistências', str(data['performance']['assists'])],
                ['Gols por Jogo', str(data['performance']['goals_per_match'])],
                ['Assistências por Jogo', str(data['performance']['assists_per_match'])],
            ]
            
            perf_table = Table(perf_data, colWidths=[3*inch, 2*inch])
            perf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(perf_table)
        else:
            story.append(Paragraph(data['performance']['note'], self.body_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

class AnalyticsDashboardService:
    def __init__(self):
        pass
    
    def create_default_dashboard(self, user):
        """Create default dashboard for new user"""
        from ..models import AnalyticsDashboard
        
        default_widgets = [
            {
                'type': 'team_form',
                'title': 'Forma dos Times Favoritos',
                'position': {'x': 0, 'y': 0, 'w': 6, 'h': 4}
            },
            {
                'type': 'match_predictions',
                'title': 'Próximas Previsões',
                'position': {'x': 6, 'y': 0, 'w': 6, 'h': 4}
            },
            {
                'type': 'value_bets',
                'title': 'Apostas de Valor',
                'position': {'x': 0, 'y': 4, 'w': 4, 'h': 3}
            },
            {
                'type': 'top_scorers',
                'title': 'Artilheiros',
                'position': {'x': 4, 'y': 4, 'w': 4, 'h': 3}
            },
            {
                'type': 'odds_tracker',
                'title': 'Rastreador de Odds',
                'position': {'x': 8, 'y': 4, 'w': 4, 'h': 3}
            }
        ]
        
        dashboard = AnalyticsDashboard.objects.create(
            user=user,
            name='Dashboard Principal',
            description='Dashboard padrão com widgets essenciais',
            widgets=default_widgets,
            is_default=True
        )
        
        return dashboard
    
    def get_widget_data(self, widget_config, user):
        """Get data for specific widget"""
        widget_type = widget_config['type']
        
        if widget_type == 'team_form':
            return self._get_team_form_data(user)
        elif widget_type == 'match_predictions':
            return self._get_match_predictions_data(user)
        elif widget_type == 'value_bets':
            return self._get_value_bets_data(user)
        elif widget_type == 'top_scorers':
            return self._get_top_scorers_data(user)
        elif widget_type == 'odds_tracker':
            return self._get_odds_tracker_data(user)
        
        return {}
    
    def _get_team_form_data(self, user):
        """Get team form data for user's favorite teams"""
        try:
            from ..models import UserAnalyticsPreference
            prefs = UserAnalyticsPreference.objects.get(user=user)
            favorite_teams = prefs.favorite_teams.all()[:5]
            
            team_data = []
            for team in favorite_teams:
                # Get recent matches
                from core.models import Match
                recent_matches = Match.objects.filter(
                    models.Q(home_team=team) | models.Q(away_team=team)
                ).order_by('-date')[:5]
                
                form = []
                points = 0
                
                for match in recent_matches:
                    is_home = match.home_team == team
                    team_score = (match.home_score or 0) if is_home else (match.away_score or 0)
                    opp_score = (match.away_score or 0) if is_home else (match.home_score or 0)
                    
                    if team_score > opp_score:
                        form.append('W')
                        points += 3
                    elif team_score < opp_score:
                        form.append('L')
                    else:
                        form.append('D')
                        points += 1
                
                team_data.append({
                    'name': team.name,
                    'form': ''.join(reversed(form)),
                    'points': points,
                    'logo': team.logo.url if team.logo else None
                })
            
            return {'teams': team_data}
            
        except:
            return {'teams': []}
    
    def _get_match_predictions_data(self, user):
        """Get upcoming match predictions"""
        from core.models import Match
        from ai_analytics.services import MatchPredictionService
        
        # Get upcoming matches
        upcoming_matches = Match.objects.filter(
            date__gte=timezone.now(),
            date__lte=timezone.now() + timedelta(days=7)
        ).order_by('date')[:5]
        
        prediction_service = MatchPredictionService()
        predictions = []
        
        for match in upcoming_matches:
            try:
                prediction = prediction_service.predict_match_outcome(match)
                predictions.append({
                    'match': {
                        'home_team': match.home_team.name,
                        'away_team': match.away_team.name,
                        'date': match.date.strftime('%d/%m %H:%M'),
                        'competition': match.competition.name
                    },
                    'prediction': {
                        'home_prob': prediction.get('home_win_probability', 0) * 100,
                        'draw_prob': prediction.get('draw_probability', 0) * 100,
                        'away_prob': prediction.get('away_win_probability', 0) * 100,
                        'confidence': prediction.get('confidence', 0) * 100
                    }
                })
            except:
                continue
        
        return {'predictions': predictions}
    
    def _get_value_bets_data(self, user):
        """Get current value betting opportunities"""
        from core.models import LiveOddsSnapshot
        
        # Get recent value bets
        value_bets = LiveOddsSnapshot.objects.filter(
            Q(is_value_bet_home=True) | Q(is_value_bet_draw=True) | Q(is_value_bet_away=True),
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-value_percentage')[:5]
        
        bets_data = []
        for bet in value_bets:
            bet_type = 'home' if bet.is_value_bet_home else ('draw' if bet.is_value_bet_draw else 'away')
            bet_name = {
                'home': bet.live_match.match.home_team.name,
                'draw': 'Empate',
                'away': bet.live_match.match.away_team.name
            }[bet_type]
            
            bets_data.append({
                'match': f"{bet.live_match.match.home_team.name} vs {bet.live_match.match.away_team.name}",
                'bet': bet_name,
                'odds': getattr(bet, f'{bet_type}_odds'),
                'value': bet.value_percentage,
                'bookmaker': bet.bookmaker.name
            })
        
        return {'value_bets': bets_data}
    
    def _get_top_scorers_data(self, user):
        """Get top scorers from favorite competitions"""
        try:
            from ..models import UserAnalyticsPreference
            from core.models import Player
            
            prefs = UserAnalyticsPreference.objects.get(user=user)
            favorite_competitions = prefs.favorite_competitions.all()
            
            # Get top scorers
            top_scorers = PlayerAnalytics.objects.filter(
                player__current_team__competitions__in=favorite_competitions
            ).order_by('-goals')[:10]
            
            scorers_data = []
            for scorer in top_scorers:
                scorers_data.append({
                    'name': scorer.player.name,
                    'team': scorer.player.current_team.name if scorer.player.current_team else 'N/A',
                    'goals': scorer.goals,
                    'matches': scorer.matches_played,
                    'avg': scorer.goals_per_match
                })
            
            return {'top_scorers': scorers_data}
            
        except:
            return {'top_scorers': []}
    
    def _get_odds_tracker_data(self, user):
        """Get odds tracking data"""
        from core.models import LiveOddsSnapshot
        
        # Get recent odds movements
        recent_odds = LiveOddsSnapshot.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=2)
        ).order_by('-timestamp')[:10]
        
        odds_data = []
        for odds in recent_odds:
            odds_data.append({
                'match': f"{odds.live_match.match.home_team.name} vs {odds.live_match.match.away_team.name}",
                'home_odds': odds.home_odds,
                'draw_odds': odds.draw_odds,
                'away_odds': odds.away_odds,
                'home_change': odds.home_odds_change,
                'draw_change': odds.draw_odds_change,
                'away_change': odds.away_odds_change,
                'timestamp': odds.timestamp.strftime('%H:%M')
            })
        
        return {'odds_movements': odds_data}
```

### 3. WhatsApp Report Integration

#### Update whatsapp_integration/services.py
```python
def generate_response(self, message_text, user):
    message_lower = message_text.lower().strip()
    
    # Report commands
    if message_lower.startswith('/relatorio') or message_lower.startswith('/report'):
        return self.handle_report_command(user, message_text)
    elif message_lower.startswith('/dashboard'):
        return self.handle_dashboard_command(user)
    
    # ... existing commands ...

def handle_report_command(self, user, message_text):
    """Handle report generation commands"""
    if not user.can_use_premium_features:
        return """🔒 Relatórios são Premium

Disponível para assinantes:
📊 Relatórios de performance
📈 Análise de jogadores
📋 Dashboard personalizado
📄 Exportação PDF/Excel

🆓 Teste 7 dias: /trial
💎 Assinar: /premium"""
    
    parts = message_text.split()[1:]  # Remove /relatorio
    
    if not parts:
        return """📊 Relatórios Disponíveis

📋 Comandos:
/relatorio time [nome] - Relatório de time
/relatorio jogador [nome] - Análise de jogador
/relatorio odds - Análise de odds
/relatorio mercado - Tendências de mercado

📈 Dashboard: /dashboard

💡 Exemplo: /relatorio time Santos"""
    
    report_type = parts[0].lower()
    
    if report_type in ['time', 'team']:
        return self.handle_team_report_request(user, parts[1:])
    elif report_type in ['jogador', 'player']:
        return self.handle_player_report_request(user, parts[1:])
    elif report_type == 'odds':
        return self.handle_odds_report_request(user)
    else:
        return "❌ Tipo de relatório não reconhecido. Use: time, jogador, odds ou mercado"

def handle_team_report_request(self, user, team_parts):
    """Handle team report request"""
    if not team_parts:
        return "❌ Especifique o time. Exemplo: /relatorio time Santos"
    
    team_name = ' '.join(team_parts)
    
    # Search for team
    from core.models import Team
    teams = Team.objects.filter(name__icontains=team_name)[:3]
    
    if not teams:
        return f"❌ Time '{team_name}' não encontrado."
    
    if len(teams) > 1:
        response = f"🔍 Encontrados {len(teams)} times:\n\n"
        for i, team in enumerate(teams, 1):
            response += f"{i}. {team.name}\n"
        response += "\nSeja mais específico ou escolha um número."
        return response
    
    team = teams[0]
    
    # Generate report asynchronously
    from analytics.tasks import generate_team_report_async
    generate_team_report_async.delay(user.user.id, team.id)
    
    return f"""📊 Gerando relatório para {team.name}

⏳ Processando dados...
📈 Analisando performance
📄 Criando PDF

📱 Você receberá o relatório em alguns minutos!

🔗 Também disponível no dashboard: /dashboard"""

def handle_player_report_request(self, user, player_parts):
    """Handle player report request"""
    if not player_parts:
        return "❌ Especifique o jogador. Exemplo: /relatorio jogador Neymar"
    
    player_name = ' '.join(player_parts)
    
    # Search for player
    from core.models import Player
    players = Player.objects.filter(name__icontains=player_name)[:3]
    
    if not players:
        return f"❌ Jogador '{player_name}' não encontrado."
    
    if len(players) > 1:
        response = f"🔍 Encontrados {len(players)} jogadores:\n\n"
        for i, player in enumerate(players, 1):
            team_name = player.current_team.name if player.current_team else 'Sem time'
            response += f"{i}. {player.name} ({team_name})\n"
        response += "\nSeja mais específico."
        return response
    
    player = players[0]
    
    # Generate report asynchronously
    from analytics.tasks import generate_player_report_async
    generate_player_report_async.delay(user.user.id, player.id)
    
    return f"""📊 Gerando análise para {player.name}

⏳ Coletando estatísticas...
📈 Analisando performance
📄 Criando relatório

📱 Você receberá a análise em alguns minutos!"""

def handle_dashboard_command(self, user):
    """Handle dashboard command"""
    if not user.can_use_premium_features:
        return """🔒 Dashboard é Premium

Funcionalidades:
📊 Widgets personalizáveis
📈 Gráficos em tempo real
🎯 Métricas dos seus times
⚽ Estatísticas de jogadores
💎 Análise de apostas

🆓 Teste 7 dias: /trial
💎 Assinar: /premium"""
    
    # Generate dashboard link
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
    
    return f"""📊 Dashboard Mark Foot

🔗 Acesse: {dashboard_url}

📈 Funcionalidades:
✅ Widgets personalizáveis
✅ Gráficos interativos
✅ Times favoritos
✅ Análise de odds
✅ Relatórios PDF

📱 Também disponível no app!"""
```

### 4. Celery Tasks for Reports

#### analytics/tasks.py
```python
from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from .services.report_service import ReportGenerationService
from whatsapp_integration.services import WhatsAppService

@shared_task
def generate_team_report_async(user_id, team_id):
    """Generate team report asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        report_service = ReportGenerationService()
        
        # Generate report for last 30 days
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
        
        report = report_service.generate_team_performance_report(
            user, team_id, date_from, date_to
        )
        
        # Send notification via WhatsApp
        whatsapp_user = user.whatsappuser
        whatsapp_service = WhatsAppService()
        
        message = f"""✅ Relatório pronto!

📊 {report.title}
📅 Período: {report.date_from.strftime('%d/%m')} a {report.date_to.strftime('%d/%m')}
⏱️ Gerado em {report.generation_time:.1f}s

🔗 Baixar PDF: {settings.FRONTEND_URL}/reports/{report.id}/pdf
📱 Ver no dashboard: {settings.FRONTEND_URL}/dashboard

📈 Dados inclusos:
✅ Performance geral
✅ Forma recente
✅ Estatísticas detalhadas
✅ Histórico de jogos"""
        
        whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
        
    except Exception as e:
        print(f"Error generating team report: {e}")

@shared_task
def generate_player_report_async(user_id, player_id):
    """Generate player report asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        report_service = ReportGenerationService()
        
        # Generate report for last 30 days
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
        
        report = report_service.generate_player_analysis_report(
            user, player_id, date_from, date_to
        )
        
        # Send notification via WhatsApp
        whatsapp_user = user.whatsappuser
        whatsapp_service = WhatsAppService()
        
        message = f"""✅ Análise pronta!

📊 {report.title}
📅 Período: {report.date_from.strftime('%d/%m')} a {report.date_to.strftime('%d/%m')}

🔗 Baixar PDF: {settings.FRONTEND_URL}/reports/{report.id}/pdf

📈 Análise incluída:
✅ Estatísticas de performance
✅ Métricas avançadas
✅ Comparação com média
✅ Evolução temporal"""
        
        whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
        
    except Exception as e:
        print(f"Error generating player report: {e}")

@shared_task
def send_weekly_reports():
    """Send weekly reports to subscribed users"""
    from whatsapp_integration.models import WhatsAppUser
    from analytics.models import UserAnalyticsPreference
    
    # Get users who want weekly reports
    weekly_users = UserAnalyticsPreference.objects.filter(
        auto_reports=True,
        report_frequency='weekly'
    )
    
    report_service = ReportGenerationService()
    whatsapp_service = WhatsAppService()
    
    for pref in weekly_users:
        try:
            user = pref.user
            whatsapp_user = user.whatsappuser
            
            if not whatsapp_user.can_use_premium_features:
                continue
            
            # Generate reports for favorite teams
            favorite_teams = pref.favorite_teams.all()[:3]  # Limit to 3 teams
            
            if favorite_teams:
                message = """📊 Relatório Semanal Mark Foot

Seus relatórios estão sendo gerados:
"""
                
                for team in favorite_teams:
                    message += f"📈 {team.name}\n"
                    
                    # Generate report
                    date_to = timezone.now().date()
                    date_from = date_to - timedelta(days=7)
                    
                    generate_team_report_async.delay(user.id, team.id)
                
                message += "\n📱 Você receberá os links em alguns minutos!"
                
                whatsapp_service.send_text_message(whatsapp_user.phone_number, message)
            
        except Exception as e:
            print(f"Error sending weekly report to user {pref.user.id}: {e}")
```

## Expected Deliverables

1. Comprehensive analytics models for teams, players, and matches
2. PDF and Excel report generation system
3. Customizable analytics dashboard
4. WhatsApp integration for report requests
5. Automated weekly/monthly reports
6. Data visualization and charts
7. Advanced performance metrics
8. Market value tracking and analysis

## Success Criteria

- PDF reports generated in under 10 seconds
- Excel exports with interactive charts
- Dashboard loads widget data in under 2 seconds
- WhatsApp report commands work instantly
- Automated reports sent weekly to premium users
- Reports include 10+ advanced metrics
- Visual charts and graphs in all reports
- Mobile-responsive dashboard interface
