# Project Overview - Mark Foot

## 🎯 Nova Visão do Projeto (Setembro 2025)
**Plataforma de inteligência esportiva via WhatsApp com chatbot AI, focada em análise de estatísticas + odds de apostas.**

Sistema revolucionário que combina coleta automatizada de dados de futebol com análises de IA conversacional, oferecendo insights únicos sobre estatísticas de jogos, jogadores e principalmente **análise inteligente de odds**, explicando o "porquê" das cotações das principais casas de apostas.

## 🚀 Diferencial Competitivo
- **WhatsApp First**: Interface conversacional natural via WhatsApp Business API
- **Odds Intelligence**: Único bot que explica WHY das odds usando IA
- **Real-time Analytics**: Dados atualizados + análises instantâneas
- **Betting Education**: Educação responsável sobre apostas e probabilidades

## 🔑 API Key Football-Data.org
- **Chave**: e87bfe5dea1746a2b4442d23ce45427c
- **Limitação**: 10 calls por minuto (Free Tier)
- **Endpoint Base**: https://api.football-data.org/v4/

## 🏆 Competições Disponíveis (Free Tier)
| Código | Nome | Região |
|--------|------|--------|
| WC | FIFA World Cup | Mundial |
| CL | UEFA Champions League | Europa |
| BL1 | Bundesliga | Alemanha |
| DED | Eredivisie | Holanda |
| BSA | Campeonato Brasileiro Série A | Brasil |
| PD | Primera División | Espanha |
| FL1 | Ligue 1 | França |
| ELC | Championship | Inglaterra |
| PPL | Primeira Liga | Portugal |
| EC | European Championship | Europa |
| SA | Serie A | Itália |
| PL | Premier League | Inglaterra |

## 🛠️ Stack Tecnológico Principal
- **Backend**: Django 4.2 + MySQL
- **Frontend**: Vue.js 3 + Vuetify + TypeScript
- **Cache/Queue**: Redis + Celery
- **Containers**: Docker + Docker Compose
- **AI/ML**: Scikit-learn + Pandas + TextBlob
- **Charts**: Chart.js + vue-chartjs

## 🏗️ Arquitetura do Sistema - WhatsApp Integration
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   Backend       │    │   External      │
│   Business API  │◄──►│   Django 4.2    │◄──►│   APIs          │
│   ChatBot AI    │    │   + AI Services │    │   Football-Data │
│   Port 443      │    │   Port 8001     │    │   + Betting APIs│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │   MySQL 8.0     │
                       │   Port 3306     │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Cache/Queue   │
                       │   Redis + Celery│
                       │   Port 6379     │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Admin Panel   │
                       │   Vue.js 3      │
                       │   Port 8080     │
                       └─────────────────┘
```

## 🎯 Objetivos Reformulados do Projeto
1. **WhatsApp Integration** - Chatbot AI conversacional para estatísticas de futebol
2. **Betting Intelligence** - Análise de odds + explicação do "porquê" das cotações
3. **Monetização B2C** - Freemium model via WhatsApp Business API
4. **Escalabilidade Global** - Multi-idioma e expansão internacional
5. **Ecosystem Partnerships** - White-label e parcerias estratégicas
6. **Responsible Gambling** - Educação sobre apostas e gestão de riscos

## 📊 Métricas de Sucesso Reformuladas
- **WhatsApp Users**: 100K usuários até final de 2025
- **Conversion Rate**: 25% free-to-premium conversion
- **API Response**: < 200ms para queries via bot
- **User Engagement**: 80%+ retention mensal
- **Revenue Growth**: R$ 375K ARR até dezembro 2025
- **International**: 3 idiomas operacionais até 2026

---
*Documento criado em: 30 de agosto de 2025*
