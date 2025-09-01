import io
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
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
from core.models import Team, Player, Match, Competition
from ai_analytics.models import MatchPrediction, PlayerRecommendation
from betting_odds.models import MatchOdds


class ReportGenerationService:
    """Service for generating analytics reports"""
    
    def __init__(self):
        self.storage_path = os.path.join(settings.MEDIA_ROOT, 'reports')
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def generate_team_report(self, user, team_id, date_from, date_to, format='pdf'):
        """Generate comprehensive team analysis report"""
        try:
            team = Team.objects.get(id=team_id)
            start_time = timezone.now()
            
            # Create report record
            report = AnalyticsReport.objects.create(
                user=user,
                title=f"Team Analysis: {team.name}",
                report_type='team_analysis',
                format=format,
                status='generating',
                date_from=date_from,
                date_to=date_to,
                parameters={
                    'team_id': team_id,
                    'team_name': team.name,
                }
            )
            
            # Collect data
            report_data = self._collect_team_data(team, date_from, date_to)
            
            # Generate file based on format
            if format == 'pdf':
                file_path = self._generate_team_pdf(report, team, report_data)
            elif format == 'excel':
                file_path = self._generate_team_excel(report, team, report_data)
            else:
                file_path = self._generate_team_json(report, team, report_data)
            
            # Update report
            generation_time = (timezone.now() - start_time).total_seconds()
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            report.status = 'completed'
            report.file_path = file_path
            report.content_data = report_data
            report.generation_time = generation_time
            report.file_size = file_size
            report.save()
            
            return report
            
        except Exception as e:
            if 'report' in locals():
                report.status = 'failed'
                report.error_message = str(e)
                report.save()
            raise e
    
    def generate_player_report(self, user, player_id, date_from, date_to, format='pdf'):
        """Generate comprehensive player analysis report"""
        try:
            player = Player.objects.get(id=player_id)
            start_time = timezone.now()
            
            # Create report record
            report = AnalyticsReport.objects.create(
                user=user,
                title=f"Player Analysis: {player.name}",
                report_type='player_analysis',
                format=format,
                status='generating',
                date_from=date_from,
                date_to=date_to,
                parameters={
                    'player_id': player_id,
                    'player_name': player.name,
                }
            )
            
            # Collect data
            report_data = self._collect_player_data(player, date_from, date_to)
            
            # Generate file based on format
            if format == 'pdf':
                file_path = self._generate_player_pdf(report, player, report_data)
            elif format == 'excel':
                file_path = self._generate_player_excel(report, player, report_data)
            else:
                file_path = self._generate_player_json(report, player, report_data)
            
            # Update report
            generation_time = (timezone.now() - start_time).total_seconds()
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            report.status = 'completed'
            report.file_path = file_path
            report.content_data = report_data
            report.generation_time = generation_time
            report.file_size = file_size
            report.save()
            
            return report
            
        except Exception as e:
            if 'report' in locals():
                report.status = 'failed'
                report.error_message = str(e)
                report.save()
            raise e
    
    def _collect_team_data(self, team, date_from, date_to):
        """Collect comprehensive team data for reports"""
        data = {
            'team_info': {
                'name': team.name,
                'founded': team.founded,
                'venue': team.venue,
                'website': team.website,
            },
            'matches': [],
            'statistics': {},
            'form_analysis': {},
            'predictions': [],
            'betting_odds': [],
        }
        
        # Get matches in date range
        matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            utc_date__date__gte=date_from,
            utc_date__date__lte=date_to
        ).order_by('-utc_date')
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        home_wins = away_wins = 0
        
        for match in matches:
            is_home = match.home_team == team
            
            match_data = {
                'date': match.utc_date.strftime('%Y-%m-%d'),
                'opponent': match.away_team.name if is_home else match.home_team.name,
                'home_away': 'Home' if is_home else 'Away',
                'score': f"{match.home_team_score or 0} - {match.away_team_score or 0}",
                'result': self._get_match_result(match, team),
                'competition': match.competition.name if match.competition else 'Unknown',
            }
            data['matches'].append(match_data)
            
            # Calculate statistics
            if match.status == 'FINISHED':
                result = self._get_match_result(match, team)
                if result == 'W':
                    wins += 1
                    if is_home:
                        home_wins += 1
                    else:
                        away_wins += 1
                elif result == 'D':
                    draws += 1
                else:
                    losses += 1
                
                team_goals = match.home_team_score if is_home else match.away_team_score
                opponent_goals = match.away_team_score if is_home else match.home_team_score
                goals_for += team_goals or 0
                goals_against += opponent_goals or 0
        
        total_matches = wins + draws + losses
        
        # Calculate statistics
        data['statistics'] = {
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against,
            'win_rate': (wins / total_matches * 100) if total_matches > 0 else 0,
            'points': wins * 3 + draws,
            'points_per_match': ((wins * 3 + draws) / total_matches) if total_matches > 0 else 0,
            'home_wins': home_wins,
            'away_wins': away_wins,
        }
        
        # Get AI predictions
        predictions = MatchPrediction.objects.filter(
            Q(match__home_team=team) | Q(match__away_team=team),
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )[:10]
        
        for pred in predictions:
            data['predictions'].append({
                'match': str(pred.match),
                'prediction_type': pred.prediction_type,
                'predicted_value': pred.predicted_value,
                'confidence_score': pred.confidence_score,
                'date': pred.created_at.strftime('%Y-%m-%d'),
            })
        
        # Get betting odds
        try:
            odds = MatchOdds.objects.filter(
                Q(match__home_team=team) | Q(match__away_team=team),
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            )[:10]
            
            for odd in odds:
                data['betting_odds'].append({
                    'match': str(odd.match),
                    'home_win_odds': float(odd.home_win_odds) if odd.home_win_odds else None,
                    'draw_odds': float(odd.draw_odds) if odd.draw_odds else None,
                    'away_win_odds': float(odd.away_win_odds) if odd.away_win_odds else None,
                    'provider': odd.provider.name if odd.provider else 'Unknown',
                })
        except:
            pass  # Handle if betting_odds not available
        
        return data
    
    def _collect_player_data(self, player, date_from, date_to):
        """Collect comprehensive player data for reports"""
        data = {
            'player_info': {
                'name': player.name,
                'position': player.position,
                'nationality': player.nationality,
                'date_of_birth': player.date_of_birth.strftime('%Y-%m-%d') if player.date_of_birth else None,
                'team': player.team.name if player.team else 'Free Agent',
            },
            'statistics': {},
            'matches': [],
            'recommendations': [],
            'market_value': {},
        }
        
        # Get player statistics
        try:
            from core.models import PlayerStatistics
            stats = PlayerStatistics.objects.filter(
                player=player,
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            ).aggregate(
                total_goals=Sum('goals'),
                total_assists=Sum('assists'),
                total_appearances=Count('id'),
                avg_rating=Avg('rating'),
            )
            
            data['statistics'] = {
                'goals': stats['total_goals'] or 0,
                'assists': stats['total_assists'] or 0,
                'appearances': stats['total_appearances'] or 0,
                'average_rating': round(stats['avg_rating'], 2) if stats['avg_rating'] else 0,
            }
        except:
            data['statistics'] = {
                'goals': 0,
                'assists': 0,
                'appearances': 0,
                'average_rating': 0,
            }
        
        # Get player matches
        if player.team:
            matches = Match.objects.filter(
                Q(home_team=player.team) | Q(away_team=player.team),
                utc_date__date__gte=date_from,
                utc_date__date__lte=date_to
            ).order_by('-utc_date')[:10]
            
            for match in matches:
                data['matches'].append({
                    'date': match.utc_date.strftime('%Y-%m-%d'),
                    'opponent': match.away_team.name if match.home_team == player.team else match.home_team.name,
                    'score': f"{match.home_team_score or 0} - {match.away_team_score or 0}",
                    'competition': match.competition.name if match.competition else 'Unknown',
                })
        
        # Get AI recommendations
        recommendations = PlayerRecommendation.objects.filter(
            player=player,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )[:5]
        
        for rec in recommendations:
            data['recommendations'].append({
                'recommendation_type': rec.recommendation_type,
                'score': rec.score,
                'reasons': rec.reasons or [],
                'date': rec.created_at.strftime('%Y-%m-%d'),
            })
        
        return data
    
    def _get_match_result(self, match, team):
        """Get match result from team perspective"""
        if match.status != 'FINISHED' or match.home_team_score is None:
            return 'N/A'
        
        is_home = match.home_team == team
        home_score = match.home_team_score
        away_score = match.away_team_score
        
        if home_score > away_score:
            return 'W' if is_home else 'L'
        elif home_score < away_score:
            return 'L' if is_home else 'W'
        else:
            return 'D'
    
    def _generate_team_pdf(self, report, team, data):
        """Generate PDF report for team analysis"""
        filename = f"team_report_{team.id}_{report.id}.pdf"
        file_path = os.path.join(self.storage_path, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"Team Analysis Report: {team.name}", title_style))
        story.append(Spacer(1, 20))
        
        # Report info
        info_data = [
            ['Report Period:', f"{report.date_from} to {report.date_to}"],
            ['Generated:', timezone.now().strftime('%Y-%m-%d %H:%M')],
            ['Generated by:', report.user.username],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Team information
        story.append(Paragraph("Team Information", styles['Heading2']))
        team_info = data['team_info']
        team_data = [
            ['Team Name:', team_info['name']],
            ['Founded:', str(team_info['founded']) if team_info['founded'] else 'Unknown'],
            ['Venue:', team_info['venue'] or 'Unknown'],
            ['Website:', team_info['website'] or 'Unknown'],
        ]
        team_table = Table(team_data, colWidths=[2*inch, 4*inch])
        team_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(team_table)
        story.append(Spacer(1, 20))
        
        # Statistics
        story.append(Paragraph("Performance Statistics", styles['Heading2']))
        stats = data['statistics']
        stats_data = [
            ['Total Matches:', str(stats['total_matches'])],
            ['Wins:', str(stats['wins'])],
            ['Draws:', str(stats['draws'])],
            ['Losses:', str(stats['losses'])],
            ['Goals For:', str(stats['goals_for'])],
            ['Goals Against:', str(stats['goals_against'])],
            ['Goal Difference:', str(stats['goal_difference'])],
            ['Win Rate:', f"{stats['win_rate']:.1f}%"],
            ['Points:', str(stats['points'])],
            ['Points per Match:', f"{stats['points_per_match']:.2f}"],
        ]
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Recent matches
        story.append(Paragraph("Recent Matches", styles['Heading2']))
        if data['matches']:
            match_data = [['Date', 'Opponent', 'H/A', 'Score', 'Result', 'Competition']]
            for match in data['matches'][:10]:  # Show last 10 matches
                match_data.append([
                    match['date'],
                    match['opponent'][:15] + '...' if len(match['opponent']) > 15 else match['opponent'],
                    match['home_away'],
                    match['score'],
                    match['result'],
                    match['competition'][:10] + '...' if len(match['competition']) > 10 else match['competition'],
                ])
            
            matches_table = Table(match_data, colWidths=[1*inch, 1.5*inch, 0.5*inch, 0.8*inch, 0.5*inch, 1.2*inch])
            matches_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(matches_table)
        else:
            story.append(Paragraph("No matches found in the selected period.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return file_path
    
    def _generate_player_pdf(self, report, player, data):
        """Generate PDF report for player analysis"""
        filename = f"player_report_{player.id}_{report.id}.pdf"
        file_path = os.path.join(self.storage_path, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"Player Analysis Report: {player.name}", title_style))
        story.append(Spacer(1, 20))
        
        # Report info
        info_data = [
            ['Report Period:', f"{report.date_from} to {report.date_to}"],
            ['Generated:', timezone.now().strftime('%Y-%m-%d %H:%M')],
            ['Generated by:', report.user.username],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Player information
        story.append(Paragraph("Player Information", styles['Heading2']))
        player_info = data['player_info']
        player_data = [
            ['Player Name:', player_info['name']],
            ['Position:', player_info['position'] or 'Unknown'],
            ['Nationality:', player_info['nationality'] or 'Unknown'],
            ['Date of Birth:', player_info['date_of_birth'] or 'Unknown'],
            ['Current Team:', player_info['team']],
        ]
        player_table = Table(player_data, colWidths=[2*inch, 4*inch])
        player_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(player_table)
        story.append(Spacer(1, 20))
        
        # Statistics
        story.append(Paragraph("Performance Statistics", styles['Heading2']))
        stats = data['statistics']
        stats_data = [
            ['Goals:', str(stats['goals'])],
            ['Assists:', str(stats['assists'])],
            ['Appearances:', str(stats['appearances'])],
            ['Average Rating:', str(stats['average_rating'])],
        ]
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        return file_path
    
    def _generate_team_excel(self, report, team, data):
        """Generate Excel report for team analysis"""
        filename = f"team_report_{team.id}_{report.id}.xlsx"
        file_path = os.path.join(self.storage_path, filename)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Team Info sheet
            team_info_df = pd.DataFrame([data['team_info']])
            team_info_df.to_excel(writer, sheet_name='Team Info', index=False)
            
            # Statistics sheet
            stats_df = pd.DataFrame([data['statistics']])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Matches sheet
            if data['matches']:
                matches_df = pd.DataFrame(data['matches'])
                matches_df.to_excel(writer, sheet_name='Matches', index=False)
            
            # Predictions sheet
            if data['predictions']:
                predictions_df = pd.DataFrame(data['predictions'])
                predictions_df.to_excel(writer, sheet_name='Predictions', index=False)
        
        return file_path
    
    def _generate_player_excel(self, report, player, data):
        """Generate Excel report for player analysis"""
        filename = f"player_report_{player.id}_{report.id}.xlsx"
        file_path = os.path.join(self.storage_path, filename)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Player Info sheet
            player_info_df = pd.DataFrame([data['player_info']])
            player_info_df.to_excel(writer, sheet_name='Player Info', index=False)
            
            # Statistics sheet
            stats_df = pd.DataFrame([data['statistics']])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Matches sheet
            if data['matches']:
                matches_df = pd.DataFrame(data['matches'])
                matches_df.to_excel(writer, sheet_name='Matches', index=False)
            
            # Recommendations sheet
            if data['recommendations']:
                recommendations_df = pd.DataFrame(data['recommendations'])
                recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return file_path
    
    def _generate_team_json(self, report, team, data):
        """Generate JSON report for team analysis"""
        filename = f"team_report_{team.id}_{report.id}.json"
        file_path = os.path.join(self.storage_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return file_path
    
    def _generate_player_json(self, report, player, data):
        """Generate JSON report for player analysis"""
        filename = f"player_report_{player.id}_{report.id}.json"
        file_path = os.path.join(self.storage_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return file_path


class AnalyticsDashboardService:
    """Service for managing analytics dashboards"""
    
    def __init__(self):
        pass
    
    def create_default_dashboard(self, user):
        """Create default dashboard for new user"""
        from ..models import AnalyticsDashboard, UserAnalyticsPreference
        
        # Create analytics preferences
        preferences, created = UserAnalyticsPreference.objects.get_or_create(
            user=user,
            defaults={
                'report_frequency': 'weekly',
                'auto_generate_reports': True,
                'email_reports': True,
                'enabled_widgets': [
                    'team_form',
                    'player_stats', 
                    'match_predictions',
                    'league_standings',
                ]
            }
        )
        
        # Create default dashboard
        dashboard, created = AnalyticsDashboard.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'My Dashboard',
                'widgets': [
                    {
                        'type': 'team_form',
                        'title': 'Team Form',
                        'position': {'x': 0, 'y': 0, 'w': 6, 'h': 4},
                        'config': {'teams': []}
                    },
                    {
                        'type': 'player_stats',
                        'title': 'Top Players',
                        'position': {'x': 6, 'y': 0, 'w': 6, 'h': 4},
                        'config': {'limit': 10}
                    },
                    {
                        'type': 'match_predictions',
                        'title': 'Match Predictions',
                        'position': {'x': 0, 'y': 4, 'w': 12, 'h': 4},
                        'config': {'days_ahead': 7}
                    },
                ],
                'layout_config': {
                    'cols': 12,
                    'margin': [10, 10],
                    'row_height': 60,
                }
            }
        )
        
        return dashboard
    
    def get_dashboard_data(self, user, dashboard_id=None):
        """Get data for dashboard widgets"""
        from ..models import AnalyticsDashboard
        
        if dashboard_id:
            dashboard = AnalyticsDashboard.objects.get(id=dashboard_id, user=user)
        else:
            dashboard = AnalyticsDashboard.objects.filter(user=user, is_default=True).first()
            if not dashboard:
                dashboard = self.create_default_dashboard(user)
        
        widget_data = {}
        
        for widget in dashboard.widgets:
            widget_type = widget.get('type')
            widget_config = widget.get('config', {})
            
            if widget_type == 'team_form':
                widget_data[widget_type] = self._get_team_form_data(widget_config)
            elif widget_type == 'player_stats':
                widget_data[widget_type] = self._get_player_stats_data(widget_config)
            elif widget_type == 'match_predictions':
                widget_data[widget_type] = self._get_match_predictions_data(widget_config)
            elif widget_type == 'league_standings':
                widget_data[widget_type] = self._get_league_standings_data(widget_config)
        
        return {
            'dashboard': dashboard,
            'data': widget_data
        }
    
    def _get_team_form_data(self, config):
        """Get team form chart data"""
        teams = config.get('teams', [])
        if not teams:
            # Get top 5 teams by recent performance
            teams = list(Team.objects.all()[:5].values_list('id', flat=True))
        
        form_data = []
        for team_id in teams:
            try:
                team = Team.objects.get(id=team_id)
                recent_matches = Match.objects.filter(
                    Q(home_team=team) | Q(away_team=team),
                    status='FINISHED'
                ).order_by('-utc_date')[:10]
                
                form = []
                for match in recent_matches:
                    result = self._get_match_result_for_team(match, team)
                    form.append(result)
                
                form_data.append({
                    'team_name': team.name,
                    'form': form[:5],  # Last 5 matches
                })
            except Team.DoesNotExist:
                continue
        
        return form_data
    
    def _get_player_stats_data(self, config):
        """Get top players statistics data"""
        limit = config.get('limit', 10)
        
        # Get players with recent statistics
        players = Player.objects.filter(
            team__isnull=False
        )[:limit]
        
        player_data = []
        for player in players:
            player_data.append({
                'name': player.name,
                'team': player.team.name if player.team else 'Free Agent',
                'position': player.position or 'Unknown',
                'nationality': player.nationality or 'Unknown',
            })
        
        return player_data
    
    def _get_match_predictions_data(self, config):
        """Get upcoming match predictions"""
        days_ahead = config.get('days_ahead', 7)
        future_date = timezone.now() + timedelta(days=days_ahead)
        
        matches = Match.objects.filter(
            utc_date__gte=timezone.now(),
            utc_date__lte=future_date,
            status__in=['SCHEDULED', 'TIMED']
        ).order_by('utc_date')[:10]
        
        predictions_data = []
        for match in matches:
            # Get AI predictions if available
            try:
                prediction = MatchPrediction.objects.filter(match=match).first()
                pred_data = {
                    'prediction_type': prediction.prediction_type,
                    'predicted_value': prediction.predicted_value,
                    'confidence': prediction.confidence_score,
                } if prediction else None
            except:
                pred_data = None
            
            predictions_data.append({
                'match': f"{match.home_team.name} vs {match.away_team.name}",
                'date': match.utc_date.strftime('%Y-%m-%d %H:%M'),
                'competition': match.competition.name if match.competition else 'Unknown',
                'prediction': pred_data,
            })
        
        return predictions_data
    
    def _get_league_standings_data(self, config):
        """Get league standings data"""
        from core.models import Standing
        
        # Get recent standings
        standings = Standing.objects.select_related('team').order_by('-position')[:10]
        
        standings_data = []
        for standing in standings:
            standings_data.append({
                'position': standing.position,
                'team': standing.team.name,
                'points': standing.points,
                'played': standing.played_games,
                'won': standing.won,
                'drawn': standing.drawn,
                'lost': standing.lost,
                'goals_for': standing.goals_for,
                'goals_against': standing.goals_against,
                'goal_difference': standing.goal_difference,
            })
        
        return standings_data
    
    def _get_match_result_for_team(self, match, team):
        """Get match result from team perspective"""
        if match.status != 'FINISHED' or match.home_team_score is None:
            return 'N/A'
        
        is_home = match.home_team == team
        home_score = match.home_team_score
        away_score = match.away_team_score
        
        if home_score > away_score:
            return 'W' if is_home else 'L'
        elif home_score < away_score:
            return 'L' if is_home else 'W'
        else:
            return 'D'
