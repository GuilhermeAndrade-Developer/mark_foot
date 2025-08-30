# Project Overview - Mark Foot

## 🎯 Visão Geral do Projeto
Sistema de coleta, armazenamento e análise de dados de futebol utilizando APIs gratuitas, com foco em escalabilidade e funcionalidades futuras.

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

## 🏗️ Arquitetura do Sistema
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   Vue.js 3      │◄──►│   Django 4.2    │◄──►│   APIs          │
│   Port 8080     │    │   Port 8001     │    │   Football-Data │
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
```

## 🎯 Objetivos do Projeto
1. **Coleta Automatizada** de dados de futebol
2. **Análise Inteligente** com Machine Learning
3. **Interface Moderna** e responsiva
4. **Escalabilidade** para milhões de usuários
5. **Monetização** sustentável
6. **Ecosystem** de parcerias

## 📊 Métricas de Sucesso
- **Uptime**: 99.9%
- **API Response**: < 200ms
- **Data Accuracy**: > 95%
- **User Engagement**: 80%+ retention
- **Revenue Growth**: 20% MoM

---
*Documento criado em: 30 de agosto de 2025*
