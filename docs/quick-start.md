# Quick Start Guide - Mark Foot Project

## Próximos Passos para Implementação

### 1. Setup do Ambiente Django 🚀

```bash
# Navegar para o diretório do projeto
cd /c/Projetos/mark_foot

# Subir os containers
docker-compose -f docker/docker-compose.dev.yml up -d

# Acessar o container Django
docker exec -it mark_foot_web_dev bash

# Dentro do container, criar o projeto Django
django-admin startproject mark_foot_backend .
python manage.py startapp core
python manage.py startapp api_integration
python manage.py startapp data_management
```

### 2. Configuração do .env

Criar arquivo `.env` no root do projeto:

```env
# Database
DB_HOST=mysql_db
DB_PORT=3306
DB_NAME=mark_foot_db_dev
DB_USER=mark_foot_user
DB_PASSWORD=mark_foot_password

# Football Data API
FOOTBALL_DATA_API_KEY=e87bfe5dea1746a2b4442d23ce45427c
FOOTBALL_DATA_BASE_URL=https://api.football-data.org/v4

# API Sports (RapidAPI) - Para quando configurar
# RAPIDAPI_KEY=your_key_here
# RAPIDAPI_HOST=api-football-v1.p.rapidapi.com

# Django
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Rate Limiting
FOOTBALL_DATA_RATE_LIMIT=10  # 10 requests per minute
```

### 3. Estrutura de Apps Django

```
mark_foot_backend/
├── core/                    # Models principais (Areas, Teams, etc.)
├── api_integration/         # Clientes para APIs externas
├── data_management/         # ETL, sync, data quality
├── api/                    # Django REST Framework endpoints
└── analytics/              # Análises e relatórios (futuro)
```

### 4. Primeiro Teste da API

```python
# Teste básico da Football Data API
import requests

headers = {
    'X-Auth-Token': 'e87bfe5dea1746a2b4442d23ce45427c'
}

# Testar conexão
response = requests.get(
    'https://api.football-data.org/v4/competitions',
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Competitions available: {len(response.json()['competitions'])}")
```

### 5. Comandos Docker Úteis

```bash
# Ver logs do Django
docker-compose -f docker/docker-compose.dev.yml logs -f web-service-dev

# Ver logs do MySQL
docker-compose -f docker/docker-compose.dev.yml logs -f mysql_db

# Acessar MySQL diretamente
docker exec -it mark_foot_mysql_dev mysql -u mark_foot_user -p mark_foot_db_dev

# Rebuild containers após mudanças
docker-compose -f docker/docker-compose.dev.yml up --build -d
```

### 6. Primeira Migration

Após criar os models básicos:

```bash
# Dentro do container Django
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## Roadmap das Próximas 2 Semanas

### Semana 1: Base Infrastructure
- [ ] Setup Django project
- [ ] Configurar conexão MySQL
- [ ] Criar models básicos (Areas, Competitions, Teams)
- [ ] Primeira integração com Football-Data API
- [ ] Implementar rate limiting

### Semana 2: Data Collection
- [ ] ETL pipeline para competitions
- [ ] ETL pipeline para teams
- [ ] ETL pipeline para matches
- [ ] Sistema de logs e monitoring
- [ ] Testes de carga de dados

---

## Checklist de Configuração

### ✅ Já Feito
- [x] Estrutura de containers Docker
- [x] docker-compose.yml configurado
- [x] Documentação do projeto
- [x] Pesquisa de APIs para jogadores
- [x] Schema do banco de dados

### 🔄 Próximos Passos
- [ ] Criar projeto Django
- [ ] Configurar settings.py
- [ ] Implementar models do banco
- [ ] Client para Football-Data API
- [ ] Primeiro sync de dados

### 🎯 Meta da Primeira Sprint
**Objetivo**: Ter dados de competições e times salvos no banco de dados através da Football-Data API.

**Deliverables**:
1. Projeto Django funcionando nos containers
2. Models de banco implementados
3. Client API funcional com rate limiting
4. Dados de pelo menos 3 competições no banco
5. Dashboard admin básico para visualizar dados

---

## Comandos de Desenvolvimento

```bash
# Iniciar ambiente de desenvolvimento
docker-compose -f docker/docker-compose.dev.yml up -d

# Ver status dos containers
docker-compose -f docker/docker-compose.dev.yml ps

# Parar ambiente
docker-compose -f docker/docker-compose.dev.yml down

# Limpar volumes (CUIDADO: apaga dados do banco)
docker-compose -f docker/docker-compose.dev.yml down -v
```

Pronto para começar a implementação! 🚀
