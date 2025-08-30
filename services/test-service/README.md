# Tests for Mark Foot Project

Este diretório contém todos os testes do projeto Mark Foot, organizados por categoria.

## Estrutura dos Testes

```
test/
├── __init__.py                    # Pacote principal de testes
├── conftest.py                    # Configuração global do pytest
├── pytest.ini                    # Configuração do pytest (movido para raiz)
├── auth/                          # Testes de autenticação
│   ├── __init__.py
│   ├── test_auth.py              # Testes de autenticação
│   ├── auth_test_complete.py     # Testes completos de auth
│   └── create_test_users.py      # Script para criar usuários de teste
├── data/                          # Testes com dados
│   ├── __init__.py
│   ├── test_data_root.py         # Dados de teste (da raiz)
│   └── test_data_web_service.py  # Dados de teste (web-service)
├── integration/                   # Testes de integração
│   ├── __init__.py
│   ├── test_sync_root.py         # Testes de sync (da raiz)
│   └── test_sync_web_service.py  # Testes de sync (web-service)
└── unit/                         # Testes unitários
    ├── __init__.py
    ├── api/
    │   └── tests.py              # Testes da API
    ├── api_integration/
    │   └── tests.py              # Testes de integração da API
    ├── chat/
    │   └── tests.py              # Testes do chat
    ├── content/
    │   └── tests.py              # Testes de conteúdo
    ├── core/
    │   └── tests.py              # Testes do core
    ├── data_management/
    │   └── tests.py              # Testes de gestão de dados
    ├── forum/
    │   └── tests.py              # Testes do fórum
    ├── gamification/
    │   ├── tests.py              # Testes de gamificação
    │   └── test_gamification_command.py  # Testes de comando
    ├── polls/
    │   └── tests.py              # Testes de enquetes
    └── social/
        └── tests.py              # Testes sociais
```

## Como Executar os Testes

### Requisitos
- Python 3.8+
- Django 4.2+
- pytest
- pytest-django

### Instalar dependências de teste
```bash
pip install pytest pytest-django pytest-cov
```

### Executar todos os testes
```bash
# Da raiz do projeto
pytest test/

# Com coverage
pytest test/ --cov=services/web-service/
```

### Executar testes específicos
```bash
# Testes de autenticação
pytest test/auth/

# Testes unitários
pytest test/unit/

# Testes de integração
pytest test/integration/

# Testes de um módulo específico
pytest test/unit/api/

# Teste específico
pytest test/unit/api/tests.py::TestAPIEndpoints::test_specific_function
```

### Executar com marcadores
```bash
# Testes unitários
pytest -m unit

# Testes de integração
pytest -m integration

# Testes de autenticação
pytest -m auth

# Testes lentos
pytest -m slow
```

## Configuração

### pytest.ini
Localizado na raiz do projeto, contém configurações do pytest incluindo:
- Paths de descoberta de testes
- Marcadores customizados
- Configurações de output
- Configurações do Django

### conftest.py
Contém fixtures globais disponíveis para todos os testes:
- `api_client`: Cliente da API REST
- `test_user`: Usuário de teste
- `authenticated_client`: Cliente autenticado
- `test_competition`: Competição de teste
- `test_team`: Time de teste
- `test_match`: Partida de teste

## Marcadores Disponíveis

- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.auth`: Testes de autenticação
- `@pytest.mark.data`: Testes de dados
- `@pytest.mark.slow`: Testes demorados
- `@pytest.mark.api`: Testes de API
- `@pytest.mark.models`: Testes de modelos
- `@pytest.mark.views`: Testes de views

## Boas Práticas

1. **Organização**: Mantenha os testes organizados por funcionalidade
2. **Nomenclatura**: Use prefixo `test_` para funções de teste
3. **Isolamento**: Cada teste deve ser independente
4. **Fixtures**: Use fixtures para dados de teste reutilizáveis
5. **Marcadores**: Use marcadores para categorizar testes
6. **Documentação**: Documente testes complexos

## Migração de Testes

Os testes foram reorganizados da seguinte forma:

### Arquivos Movidos:
- `test_data.py` → `test/data/test_data_root.py`
- `test_sync.py` → `test/integration/test_sync_root.py`
- `services/web-service/test_*.py` → Reorganizados em `test/`
- `services/web-service/*/tests.py` → `test/unit/*/tests.py`

### Benefícios da Reorganização:
- ✅ Centralização de todos os testes
- ✅ Organização por tipo (unit, integration, auth, data)
- ✅ Configuração unificada do pytest
- ✅ Fixtures globais reutilizáveis
- ✅ Estrutura consistente e escalável
