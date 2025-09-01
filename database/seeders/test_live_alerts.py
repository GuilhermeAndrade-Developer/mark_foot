#!/usr/bin/env python3
"""
Teste do sistema de alertas de jogos ao vivo - Mark Foot
Este script simula eventos e testa os alertas automáticos
"""

import os
import sys
import django

# Configuração do Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings')
django.setup()

from django.utils import timezone
from core.models import LiveMatch, LiveMatchEvent, MatchAlert
from core.services.live_data_service import LiveDataService
from whatsapp_integration.models import WhatsAppUser
import random


def simulate_goal_event():
    """Simula um gol em um jogo ao vivo"""
    print("⚽ Simulando evento de gol...")
    
    # Pegar um jogo ao vivo ativo
    live_match = LiveMatch.objects.filter(is_active=True).first()
    
    if not live_match:
        print("❌ Nenhum jogo ao vivo ativo encontrado")
        return
    
    print(f"🏟️ Jogo: {live_match.match.home_team.name} vs {live_match.match.away_team.name}")
    print(f"⏱️ Minuto: {live_match.minute}")
    
    # Simular gol do time da casa
    old_home_score = live_match.home_score
    old_away_score = live_match.away_score
    
    live_match.home_score += 1
    live_match.minute += random.randint(1, 5)
    live_match.save()
    
    print(f"🎯 Novo placar: {live_match.home_score} x {live_match.away_score}")
    
    # Criar evento
    event = LiveMatchEvent.objects.create(
        live_match=live_match,
        event_type='GOAL',
        minute=live_match.minute,
        team=live_match.match.home_team,
        player_name='Teste Player',
        description=f"Gol! {live_match.match.home_team.name}"
    )
    
    print(f"✅ Evento criado: {event}")
    
    # Usar o serviço para criar alerta
    live_service = LiveDataService()
    live_service._handle_goal_scored(live_match, old_home_score, old_away_score)
    
    print("📱 Alerta de gol criado!")


def simulate_red_card_event():
    """Simula um cartão vermelho"""
    print("🟥 Simulando cartão vermelho...")
    
    live_match = LiveMatch.objects.filter(is_active=True).first()
    
    if not live_match:
        print("❌ Nenhum jogo ao vivo ativo encontrado")
        return
    
    # Atualizar estatísticas
    live_match.away_red_cards += 1
    live_match.minute += random.randint(1, 3)
    live_match.save()
    
    # Criar evento
    event = LiveMatchEvent.objects.create(
        live_match=live_match,
        event_type='RED_CARD',
        minute=live_match.minute,
        team=live_match.match.away_team,
        player_name='Test Player 2',
        description=f"Cartão Vermelho - {live_match.match.away_team.name}"
    )
    
    # Usar o serviço para criar alerta
    live_service = LiveDataService()
    live_service.create_red_card_alert(live_match, None, live_match.match.away_team)
    
    print(f"✅ Evento e alerta de cartão vermelho criados!")


def list_recent_alerts():
    """Lista alertas recentes"""
    print("📋 Alertas recentes:")
    
    recent_alerts = MatchAlert.objects.order_by('-created_at')[:10]
    
    for alert in recent_alerts:
        status = "✅ Enviado" if alert.is_sent else "⏳ Pendente"
        print(f"  {status} - {alert.get_alert_type_display()}: {alert.title}")
        print(f"    {alert.message[:100]}...")
        print(f"    Criado: {alert.created_at.strftime('%H:%M:%S')}")
        print()


def create_test_users():
    """Cria usuários de teste para receber alertas"""
    print("👥 Criando usuários de teste...")
    
    test_users = [
        {
            'phone_number': '+5511999999001',
            'display_name': 'Premium User',
            'subscription_status': 'premium'
        },
        {
            'phone_number': '+5511999999002',
            'display_name': 'Pro User',
            'subscription_status': 'pro'
        },
        {
            'phone_number': '+5511999999003',
            'display_name': 'Free User',
            'subscription_status': 'free'
        }
    ]
    
    for user_data in test_users:
        user, created = WhatsAppUser.objects.get_or_create(
            phone_number=user_data['phone_number'],
            defaults=user_data
        )
        
        if created:
            print(f"  ✅ Usuário criado: {user.display_name} ({user.subscription_status})")
        else:
            print(f"  ℹ️ Usuário existente: {user.display_name} ({user.subscription_status})")
    
    print(f"📊 Total de usuários WhatsApp: {WhatsAppUser.objects.count()}")


def show_live_matches_status():
    """Mostra o status atual dos jogos ao vivo"""
    print("🔴 Status dos jogos ao vivo:")
    
    live_matches = LiveMatch.objects.filter(is_active=True)
    
    for live_match in live_matches:
        match = live_match.match
        print(f"🏟️ {match.home_team.name} {live_match.home_score} x {live_match.away_score} {match.away_team.name}")
        print(f"  ⏱️ {live_match.minute}' - {live_match.get_status_display()}")
        print(f"  📊 Posse: {live_match.home_possession:.0f}% x {live_match.away_possession:.0f}%")
        print(f"  🎯 Finalizações: {live_match.home_shots} x {live_match.away_shots}")
        print(f"  🟨 Cartões: {live_match.home_yellow_cards} x {live_match.away_yellow_cards}")
        print(f"  🟥 Vermelhos: {live_match.home_red_cards} x {live_match.away_red_cards}")
        
        # Eventos recentes
        recent_events = live_match.events.order_by('-minute')[:3]
        if recent_events.exists():
            print("  📝 Eventos recentes:")
            for event in recent_events:
                print(f"    {event.minute}' - {event.get_event_type_display()}")
        print()


def main():
    """Menu principal"""
    print("🔴 TESTE: Sistema de Alertas de Jogos ao Vivo")
    print("=" * 50)
    
    while True:
        print("\nOpções:")
        print("1. Mostrar status dos jogos ao vivo")
        print("2. Simular gol")
        print("3. Simular cartão vermelho") 
        print("4. Criar usuários de teste")
        print("5. Listar alertas recentes")
        print("0. Sair")
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                show_live_matches_status()
            elif choice == "2":
                simulate_goal_event()
            elif choice == "3":
                simulate_red_card_event()
            elif choice == "4":
                create_test_users()
            elif choice == "5":
                list_recent_alerts()
            elif choice == "0":
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    main()
