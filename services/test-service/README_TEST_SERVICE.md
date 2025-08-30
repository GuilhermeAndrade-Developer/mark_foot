# 🧪 Mark Foot Test Service

Microserviço dedicado para execução de testes do projeto Mark Foot.

## 📁 Estrutura

```
test-service/
├── 📁 auth/              # Testes de autenticação
├── 📁 data/              # Testes de dados
├── 📁 integration/       # Testes de integração
├── 📁 unit/              # Testes unitários
│   ├── 📁 api/           # Testes da API
│   ├── 📁 core/          # Testes do core
│   ├── 📁 gamification/  # Testes de gamificação
│   ├── 📁 social/        # Testes sociais
│   └── ...
├── 🐳 Dockerfile         # Container de testes
├── 📋 requirements.txt   # Dependências Python
├── ⚙️ pytest.ini        # Configuração pytest
├── 🔧 test_settings.py   # Settings Django para testes
├── 🚀 run_tests.sh       # Script de execução (Linux/Mac)
├── 🚀 run_tests.ps1      # Script de execução (Windows)
└── 📊 Makefile          # Comandos make
```

## 🚀 Como Usar

### Método 1: Docker Compose (Recomendado)

```bash
# Executar todos os testes
docker-compose -f docker/docker-compose.dev.yml --profile testing up test-service-dev

# Executar testes específicos
docker-compose -f docker/docker-compose.dev.yml run --rm test-service-dev python -m pytest unit/ -v
```

### Método 2: Makefile

```bash
cd services/test-service

# Ver comandos disponíveis
make help

# Executar todos os testes
make test

# Executar testes unitários
make test-unit

# Executar testes de integração
make test-integration

# Executar com cobertura
make test-coverage

# Executar em paralelo
make test-parallel
```

### Método 3: Scripts Diretos

**Linux/Mac:**
```bash
cd services/test-service
./run_tests.sh --type unit --parallel
```

**Windows:**
```powershell
cd services\test-service
.\run_tests.ps1 -TestType unit -Parallel
```

## 🏷️ Tipos de Teste

| Tipo | Descrição | Comando |
|------|-----------|---------|
| `unit` | Testes unitários | `pytest unit/ -m unit` |
| `integration` | Testes de integração | `pytest integration/ -m integration` |
| `auth` | Testes de autenticação | `pytest auth/ -m auth` |
| `api` | Testes de API | `pytest -m api` |
| `gamification` | Testes de gamificação | `pytest unit/gamification/ -m gamification` |
| `social` | Testes sociais | `pytest unit/social/ -m social` |
| `data` | Testes de dados | `pytest data/ -m data` |

## 📊 Relatórios

### Cobertura de Código
- **HTML**: `htmlcov/index.html`
- **Terminal**: Exibido automaticamente com `--cov-report=term-missing`

### Logs de Teste
- **Container**: `docker logs mark_foot_test_service_dev`
- **Arquivo**: Disponível no volume `test_reports`

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
DJANGO_SETTINGS_MODULE=test_settings
DB_HOST=mark_foot_mysql_dev
DB_NAME=mark_foot_db_dev
DB_USER=mark_foot_user
DB_PASSWORD=mark_foot_password
REDIS_URL=redis://mark_foot_redis_dev:6379/0
```

### Marcadores Pytest

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.api
@pytest.mark.gamification
@pytest.mark.social
@pytest.mark.data
@pytest.mark.slow
```

## 🔧 Desenvolvimento

### Adicionar Novos Testes

1. **Teste Unitário**: Coloque em `unit/<módulo>/`
2. **Teste Integração**: Coloque em `integration/`
3. **Teste Autenticação**: Coloque em `auth/`

### Exemplo de Teste

```python
import pytest
from django.test import TestCase

@pytest.mark.unit
@pytest.mark.api
class TestApiViews(TestCase):
    def test_api_endpoint(self):
        # Seu teste aqui
        assert True
```

## 📈 CI/CD

O serviço de testes está configurado para:

- ✅ Execução automática em containers
- ✅ Relatórios de cobertura
- ✅ Execução paralela
- ✅ Marcadores para filtrar testes
- ✅ Integração com banco de dados de teste
- ✅ Isolamento de ambiente

## 🐛 Troubleshooting

### Problemas Comuns

**Erro de conexão com BD:**
```bash
# Verificar se o MySQL está rodando
docker ps | grep mysql

# Reiniciar serviços
make down && make up
```

**Testes lentos:**
```bash
# Usar execução paralela
make test-parallel

# Executar apenas testes rápidos
pytest -m "not slow"
```

**Limpar cache:**
```bash
# Limpar containers e volumes
make clean

# Reconstruir imagem
make build
```

## 📞 Suporte

Para problemas com testes, verifique:

1. 📋 Logs do container: `make logs`
2. 🔍 Status dos serviços: `docker ps`
3. 🗄️ Conexão com BD: Variáveis de ambiente
4. 📊 Relatórios: `htmlcov/index.html`

---

**Desenvolvido com ❤️ para o projeto Mark Foot** 🏆
