# Arquitetura Técnica Detalhada - Mark Foot

## 🏗️ Visão Geral da Arquitetura

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Vue.js 3 + Vuetify]
        PWA[Progressive Web App]
        MOBILE[React Native - Futuro]
    end
    
    subgraph "API Gateway"
        NGINX[Nginx Reverse Proxy]
        LB[Load Balancer]
        RATE[Rate Limiting]
    end
    
    subgraph "Backend Services"
        DJANGO[Django 4.2 REST API]
        CELERY[Celery Workers]
        AI[AI/ML Services]
        CHAT[Chat Service]
    end
    
    subgraph "Data Layer"
        MYSQL[(MySQL 8.0)]
        REDIS[(Redis Cache)]
        ELASTIC[(Elasticsearch - Futuro)]
    end
    
    subgraph "External APIs"
        FOOTBALL[Football-Data.org]
        SPORTSDB[TheSportsDB]
        SOCIAL[Social Media APIs]
    end
    
    FE --> NGINX
    PWA --> NGINX
    NGINX --> DJANGO
    DJANGO --> MYSQL
    DJANGO --> REDIS
    CELERY --> REDIS
    AI --> MYSQL
    DJANGO --> FOOTBALL
    DJANGO --> SPORTSDB
```

## 🛠️ Stack Tecnológico Completo

### Frontend
```yaml
Framework: Vue.js 3.4.0
UI Library: Vuetify 3.4.0
Language: TypeScript 5.0
State Management: Pinia
HTTP Client: Axios
Charts: Chart.js + vue-chartjs
Build Tool: Vite 5.0
CSS: SCSS + Material Design
PWA: Vite PWA Plugin
```

### Backend
```yaml
Framework: Django 4.2
API: Django REST Framework 3.14
Authentication: JWT (djangorestframework-simplejwt)
Database ORM: Django ORM
Serialization: DRF Serializers
Documentation: drf-spectacular (Swagger)
Validation: Django Validators + Custom
Permissions: DRF Permissions
Pagination: DRF Pagination
```

### Database & Cache
```yaml
Primary DB: MySQL 8.0
Cache: Redis 7.0
Queue Broker: Redis
Search Engine: Elasticsearch (Planejado)
Time Series: InfluxDB (Planejado)
File Storage: Django Storage + S3 (Futuro)
```

### AI/ML Stack
```yaml
Framework: Scikit-learn 1.3
Data Processing: Pandas 2.0, NumPy 1.24
NLP: TextBlob, VADER Sentiment
Models: Random Forest, K-means, Isolation Forest
Deployment: Django Services
Storage: PostgreSQL JSON Fields
```

### DevOps & Infrastructure
```yaml
Containers: Docker + Docker Compose
Orchestration: Kubernetes (Planejado)
CI/CD: GitHub Actions (Planejado)
Monitoring: Prometheus + Grafana (Planejado)
Logging: ELK Stack (Planejado)
Cloud: AWS/GCP (Futuro)
```

## 📊 Estrutura de Banco de Dados

### Core Tables
```sql
-- Tabelas principais de futebol
Areas (id, name, code, flag, parent_area_id)
Competitions (id, name, code, type, area_id, current_season_id)
Seasons (id, start_date, end_date, current_matchday, competition_id)
Teams (id, name, short_name, tla, crest, area_id, venue, website)
Players (id, name, position, date_of_birth, nationality, team_id)
Matches (id, competition_id, season_id, matchday, home_team_id, away_team_id, 
         utc_date, status, stage, group, last_updated, score)
Standings (id, competition_id, season_id, stage, type, group, table)
```

### AI/ML Tables
```sql
-- Tabelas especializadas em IA
MatchPredictions (id, match_id, home_win_prob, draw_prob, away_win_prob, confidence)
PlayerRecommendations (id, user_id, player_id, similarity_score, reasons)
SentimentAnalysis (id, content_text, platform, sentiment_score, keywords)
InjuryPredictions (id, player_id, risk_score, factors, recommendations)
MarketValueAnalysis (id, player_id, predicted_value, confidence_interval)
PlayStyleClusters (id, player_id, cluster_id, style_features, cluster_center)
AnomalyDetections (id, entity_type, entity_id, anomaly_score, detection_type)
TransferSimulations (id, player_id, target_team_id, success_probability)
```

### Social & Gamification Tables
```sql
-- Gamificação
UserProfiles (id, user_id, points, level, badges, preferences)
GameChallenges (id, title, description, rules, start_date, end_date, reward_points)
FantasyLeagues (id, name, type, start_date, end_date, rules, prize_pool)
UserBadges (id, user_id, badge_id, earned_date, criteria_met)
PointTransactions (id, user_id, amount, transaction_type, description)

-- Social Features
ChatRooms (id, name, room_type, competition_id, team_id, is_active)
ChatMessages (id, room_id, user_id, content, message_type, timestamp)
ForumCategories (id, name, description, icon, is_active, sort_order)
ForumTopics (id, category_id, title, description, author_id, is_pinned)
UserArticles (id, author_id, title, content, category_id, status, views)
Polls (id, question, description, poll_type, start_date, end_date, is_active)
```

## 🔄 Fluxo de Dados

### Data Collection Pipeline
```python
# 1. External API Collection
Football_Data_API -> RateLimiter -> DataValidator -> ETL_Pipeline

# 2. Data Processing
ETL_Pipeline -> DataTransformer -> ConflictResolver -> DatabaseWriter

# 3. AI Processing
DatabaseReader -> MLPreprocessor -> AIModels -> PredictionStorage

# 4. Frontend Consumption
API_Endpoints -> Serializers -> JSON_Response -> Vue_Components
```

### Real-time Updates
```python
# Celery Tasks Schedule
Live_Matches_Update: every 30 minutes
Daily_Standings_Update: daily at 2 AM
Weekly_Teams_Refresh: Sundays at 1 AM
Monthly_Full_Sync: 1st of month at midnight
AI_Analysis_Update: daily at 3 AM
Player_Data_Sync: weekly on Wednesdays
Health_Checks: every 5 minutes
Data_Integrity_Validation: daily at 4 AM
```

## 🔐 Segurança e Autenticação

### Authentication Flow
```yaml
Registration: Email verification required
Login: JWT access token (15 min) + refresh token (7 days)
Password Reset: Secure token via email
2FA: TOTP support (futuro)
OAuth: Google/Facebook integration (futuro)
```

### API Security
```python
# Implementações de segurança
Rate_Limiting: per IP and per user
CORS_Headers: configured for frontend domains
CSRF_Protection: enabled for state-changing operations
SQL_Injection_Prevention: Django ORM parameterized queries
XSS_Protection: DRF serializer validation
Input_Validation: comprehensive validation layer
Permission_Classes: role-based access control
```

### Data Protection
```yaml
LGPD_Compliance: user data anonymization and deletion
Encryption_at_Rest: database field-level encryption (planejado)
HTTPS_Only: SSL certificate required
Audit_Logging: user action tracking
Data_Retention: configurable retention policies
Privacy_Controls: user privacy dashboard
```

## 📈 Performance e Escalabilidade

### Database Optimization
```sql
-- Indexes estratégicos implementados
CREATE INDEX idx_matches_competition_season ON matches(competition_id, season_id);
CREATE INDEX idx_standings_competition_team ON standings(competition_id, team_id);
CREATE INDEX idx_players_team_position ON players(team_id, position);
CREATE INDEX idx_api_sync_log_endpoint_timestamp ON api_sync_log(endpoint, timestamp);

-- Query optimization
SELECT teams.*, standings.position 
FROM teams 
INNER JOIN standings ON teams.id = standings.team_id 
WHERE standings.competition_id = %s 
ORDER BY standings.position;
```

### Caching Strategy
```python
# Redis caching implementation
Competitions_List: 1 hour TTL
Team_Details: 6 hours TTL
Match_Results: 1 hour TTL (live matches: 5 minutes)
Player_Stats: 12 hours TTL
AI_Predictions: 24 hours TTL
User_Sessions: 30 minutes TTL
API_Responses: 15 minutes TTL
```

### API Performance
```yaml
Response_Times:
  Database_Queries: <50ms average
  API_Endpoints: <200ms average
  Complex_Analytics: <500ms average
  ML_Predictions: <1000ms average

Optimization_Techniques:
  - Database query optimization
  - Redis caching layer
  - API response compression
  - Lazy loading for large datasets
  - Pagination for list endpoints
```

## 🚀 Deployment e DevOps

### Container Architecture
```yaml
# docker-compose.yml services
frontend: Vue.js development server (port 8080)
backend: Django + Gunicorn (port 8001)
database: MySQL 8.0 (port 3306)
redis: Redis cache/queue (port 6379)
celery: Background task workers
celery-beat: Task scheduler
nginx: Reverse proxy (port 80, 443)
```

### Environment Configuration
```bash
# Production environment variables
DATABASE_URL=mysql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
SECRET_KEY=production-secret-key
ALLOWED_HOSTS=markfoot.com,api.markfoot.com
DEBUG=False
CELERY_BROKER_URL=redis://host:port/1
EMAIL_HOST=smtp.gmail.com
FOOTBALL_DATA_API_KEY=production-key
```

### Monitoring & Observability
```yaml
Health_Checks:
  - Database connection status
  - Redis connection status
  - External API availability
  - Celery worker status
  - Disk space monitoring
  - Memory usage tracking

Logging_Levels:
  Production: INFO and above
  Development: DEBUG and above
  Critical_Errors: immediate notification
  Performance_Metrics: daily reports
```

## 🔮 Arquitetura Futura (Fases 7-8)

### Microservices Transition
```yaml
Auth_Service: JWT + OAuth management
Data_Collection_Service: API integrations
AI_ML_Service: machine learning pipeline
Chat_Service: real-time messaging
Notification_Service: push notifications
Payment_Service: subscription management
Analytics_Service: business intelligence
```

### Cloud Infrastructure
```yaml
Container_Orchestration: Kubernetes
Service_Mesh: Istio
API_Gateway: Kong or AWS API Gateway
Database: RDS MySQL + Redis ElastiCache
Search: Elasticsearch Service
Monitoring: Prometheus + Grafana
Logging: ELK Stack
CDN: CloudFlare or AWS CloudFront
```

---
*Documentação técnica atualizada em: 30 de agosto de 2025*
