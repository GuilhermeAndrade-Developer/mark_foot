#!/usr/bin/env python3
"""
Seeder para dados de jogos ao vivo - Mark Foot
Este seeder cria dados de exemplo para testar o sistema de monitoramento ao vivo
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuração do Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.utils import timezone
from core.models import Match, Team, Competition, Season, LiveMatch, LiveMatchEvent, LiveOddsSnapshot, MatchAlert
from ai_analytics.models import MatchPrediction
import random


def create_live_match_data():
    """Cria dados de exemplo para jogos ao vivo"""
    print("🔴 Criando dados de jogos ao vivo...")
    
    # Buscar partidas agendadas para hoje
    today = timezone.now().date()
    scheduled_matches = Match.objects.filter(
        utc_date__date=today,
        status='SCHEDULED'
    )[:3]  # Pegar até 3 partidas
    
    if not scheduled_matches.exists():
        print("❌ Nenhuma partida agendada para hoje. Criando partidas de exemplo...")
        create_sample_matches()
        scheduled_matches = Match.objects.filter(
            utc_date__date=today,
            status='SCHEDULED'
        )[:3]
    
    created_count = 0
    for match in scheduled_matches:
        # Criar dados de live match
        live_match, created = LiveMatch.objects.get_or_create(
            match=match,
            defaults={
                'status': random.choice(['FIRST_HALF', 'SECOND_HALF', 'HALF_TIME']),
                'minute': random.randint(1, 90),
                'added_time': random.randint(0, 5),
                'home_score': random.randint(0, 3),
                'away_score': random.randint(0, 3),
                'home_possession': random.uniform(35, 65),
                'away_possession': random.uniform(35, 65),
                'home_shots': random.randint(3, 15),
                'away_shots': random.randint(3, 15),
                'home_shots_on_target': random.randint(1, 8),
                'away_shots_on_target': random.randint(1, 8),
                'home_corners': random.randint(0, 8),
                'away_corners': random.randint(0, 8),
                'home_fouls': random.randint(5, 15),
                'away_fouls': random.randint(5, 15),
                'home_yellow_cards': random.randint(0, 3),
                'away_yellow_cards': random.randint(0, 3),
                'home_red_cards': random.randint(0, 1),
                'away_red_cards': random.randint(0, 1),
                'is_active': True,
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✅ Live match criado: {live_match}")
            
            # Criar eventos para o jogo
            create_match_events(live_match)
            
            # Criar snapshots de odds
            create_odds_snapshots(live_match)
            
            # Criar alertas
            create_match_alerts(match)
            
            # Criar previsões AI
            create_ai_predictions(match)
    
    print(f"✅ {created_count} jogos ao vivo criados com sucesso!")


def create_sample_matches():
    """Cria partidas de exemplo para hoje"""
    print("📅 Criando partidas de exemplo...")
    
    # Buscar times
    teams = list(Team.objects.all()[:10])
    if len(teams) < 4:
        print("❌ Poucos times disponíveis. Execute primeiro os seeders de times.")
        return
    
    # Buscar competição
    competition = Competition.objects.first()
    if not competition:
        print("❌ Nenhuma competição disponível. Execute primeiro os seeders de competições.")
        return
    
    # Buscar season
    season = Season.objects.filter(competition=competition).first()
    if not season:
        print("❌ Nenhuma season disponível. Execute primeiro os seeders de seasons.")
        return
    
    # Criar 3 partidas para hoje
    today = timezone.now()
    for i in range(3):
        match_time = today.replace(hour=15+i*2, minute=0, second=0, microsecond=0)
        home_team = teams[i*2]
        away_team = teams[i*2+1]
        
        # Usar um ID único baseado no timestamp
        match_id = int(match_time.timestamp()) + i
        
        match, created = Match.objects.get_or_create(
            id=match_id,
            defaults={
                'home_team': home_team,
                'away_team': away_team,
                'utc_date': match_time,
                'competition': competition,
                'season': season,
                'status': 'SCHEDULED',
                'matchday': 1,
            }
        )
        
        if created:
            print(f"  ✅ Partida criada: {match}")


def create_match_events(live_match):
    """Cria eventos para um jogo ao vivo"""
    events_data = [
        ('KICK_OFF', 0, 'Início do jogo'),
        ('GOAL', random.randint(15, 45), f'Gol de {live_match.match.home_team.name}'),
        ('YELLOW_CARD', random.randint(25, 60), 'Cartão amarelo'),
        ('GOAL', random.randint(50, 85), f'Gol de {live_match.match.away_team.name}'),
    ]
    
    if live_match.minute >= 45:
        events_data.append(('HALF_TIME', 45, 'Fim do primeiro tempo'))
    
    if live_match.minute >= 90:
        events_data.append(('FULL_TIME', 90, 'Fim do jogo'))
    
    for event_type, minute, description in events_data:
        if minute <= live_match.minute:
            LiveMatchEvent.objects.get_or_create(
                live_match=live_match,
                event_type=event_type,
                minute=minute,
                defaults={
                    'description': description,
                    'team': live_match.match.home_team if 'home' in description.lower() else live_match.match.away_team,
                }
            )


def create_odds_snapshots(live_match):
    """Cria snapshots de odds para um jogo ao vivo"""
    # Criar snapshots a cada 10 minutos do jogo
    for minute in range(0, live_match.minute + 1, 10):
        # Odds que variam durante o jogo
        base_home = 2.0 + random.uniform(-0.5, 0.5)
        base_draw = 3.2 + random.uniform(-0.3, 0.3)
        base_away = 3.5 + random.uniform(-0.5, 0.5)
        
        # Ajustar odds baseado no placar atual
        score_diff = live_match.home_score - live_match.away_score
        if score_diff > 0:  # Home winning
            base_home -= 0.3
            base_away += 0.3
        elif score_diff < 0:  # Away winning
            base_away -= 0.3
            base_home += 0.3
        
        LiveOddsSnapshot.objects.get_or_create(
            live_match=live_match,
            minute=minute,
            defaults={
                'home_odds': round(base_home, 2),
                'draw_odds': round(base_draw, 2),
                'away_odds': round(base_away, 2),
                'over_2_5_odds': round(1.8 + random.uniform(-0.2, 0.2), 2),
                'under_2_5_odds': round(2.0 + random.uniform(-0.2, 0.2), 2),
                'both_teams_score_yes': round(1.7 + random.uniform(-0.2, 0.2), 2),
                'both_teams_score_no': round(2.1 + random.uniform(-0.2, 0.2), 2),
                'value_percentage': random.uniform(0, 20),
                'is_value_bet': random.choice([True, False]),
            }
        )


def create_match_alerts(match):
    """Cria alertas de exemplo para uma partida"""
    alert_types = [
        ('MATCH_START', 'HIGH', 'Jogo Iniciado!', f'🚀 {match.home_team.name} vs {match.away_team.name} começou!'),
        ('GOAL', 'HIGH', 'Gol!', f'⚽ Gol no jogo {match.home_team.name} vs {match.away_team.name}!'),
        ('HALF_TIME', 'MEDIUM', 'Intervalo', f'📊 Intervalo - {match.home_team.name} vs {match.away_team.name}'),
        ('VALUE_BET', 'URGENT', 'Value Bet!', f'💰 Oportunidade de value bet detectada!'),
    ]
    
    for alert_type, priority, title, message in alert_types:
        MatchAlert.objects.get_or_create(
            match=match,
            alert_type=alert_type,
            defaults={
                'priority': priority,
                'title': title,
                'message': message,
                'target_subscription_levels': ['premium', 'pro'],
                'is_sent': random.choice([True, False]),
            }
        )


def create_ai_predictions(match):
    """Cria previsões AI de exemplo para uma partida"""
    predictions_data = [
        {
            'type': 'RESULT',
            'value': 'HOME_WIN',
            'confidence': random.uniform(0.6, 0.9),
            'features': {
                'home_win_probability': random.uniform(0.4, 0.7),
                'draw_probability': random.uniform(0.2, 0.4),
                'away_win_probability': random.uniform(0.2, 0.4),
                'home_team_form': random.uniform(0.5, 1.0),
                'away_team_form': random.uniform(0.3, 0.8),
            }
        },
        {
            'type': 'GOALS',
            'value': '2.5',
            'confidence': random.uniform(0.5, 0.8),
            'features': {
                'predicted_total_goals': random.uniform(2.0, 3.5),
                'both_teams_score_prob': random.uniform(0.5, 0.8),
            }
        }
    ]
    
    for pred_data in predictions_data:
        MatchPrediction.objects.get_or_create(
            match=match,
            prediction_type=pred_data['type'],
            defaults={
                'predicted_value': pred_data['value'],
                'confidence_score': pred_data['confidence'],
                'model_version': 'v1.0_seeder',
                'features_used': pred_data['features'],
            }
        )


def cleanup_old_live_data():
    """Remove dados antigos de jogos ao vivo"""
    print("🧹 Limpando dados antigos...")
    
    # Remove live matches inativos há mais de 1 dia
    cutoff = timezone.now() - timedelta(days=1)
    
    old_live_matches = LiveMatch.objects.filter(
        is_active=False,
        updated_at__lt=cutoff
    )
    
    count = old_live_matches.count()
    if count > 0:
        old_live_matches.delete()
        print(f"  ✅ {count} jogos ao vivo antigos removidos")
    
    # Remove alertas antigos (mais de 7 dias)
    old_alerts_cutoff = timezone.now() - timedelta(days=7)
    old_alerts = MatchAlert.objects.filter(created_at__lt=old_alerts_cutoff)
    
    alert_count = old_alerts.count()
    if alert_count > 0:
        old_alerts.delete()
        print(f"  ✅ {alert_count} alertas antigos removidos")


def main():
    """Função principal do seeder"""
    print("🔴 SEEDER: Dados de Jogos ao Vivo - Mark Foot")
    print("=" * 50)
    
    try:
        # Limpar dados antigos primeiro
        cleanup_old_live_data()
        
        # Criar novos dados
        create_live_match_data()
        
        print("\n" + "=" * 50)
        print("✅ Seeder de jogos ao vivo executado com sucesso!")
        print("\nDados criados:")
        print(f"  - Live Matches: {LiveMatch.objects.filter(is_active=True).count()}")
        print(f"  - Live Events: {LiveMatchEvent.objects.count()}")
        print(f"  - Odds Snapshots: {LiveOddsSnapshot.objects.count()}")
        print(f"  - Match Alerts: {MatchAlert.objects.count()}")
        print(f"  - AI Predictions: {MatchPrediction.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erro ao executar seeder: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
