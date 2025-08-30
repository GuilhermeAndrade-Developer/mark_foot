# Correções do Erro do Celery Beat

## Problema Original
```
ProgrammingError: (1146, "Table 'mark_foot_db_dev.django_celery_beat_periodictask' doesn't exist")
```

O container `mark_foot_celery_beat_dev` estava reiniciando continuamente devido a este erro.

## Causa Raiz
1. **Timing de inicialização**: Os containers Django/Celery iniciavam antes do MySQL estar completamente pronto
2. **Migrações não executadas**: As tabelas do `django_celery_beat` não eram criadas antes do Celery Beat tentar acessá-las
3. **Erro no script de inicialização**: O banco era nomeado diferentemente no script de init

## Soluções Implementadas

### 1. Script de Espera do Banco (`wait-for-db.py`)
- Criado script que aguarda o banco estar disponível antes de prosseguir
- Tenta conectar ao banco até 30 vezes com intervalo de 2 segundos
- Localização: `services/web-service/wait-for-db.py`

### 2. Correção dos Docker Compose

#### Desenvolvimento (`docker-compose.dev.yml`)
```yaml
command: sh -c "python wait-for-db.py && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

#### Produção (`docker-compose.prod.yml`)
```yaml
command: sh -c "python wait-for-db.py && python manage.py migrate && gunicorn mark_foot_backend.wsgi:application --bind 0.0.0.0:8000 --workers 3"
```

### 3. Dependências Ajustadas
- `celery-worker-dev` agora depende de `web-service-dev`
- `celery-beat-dev` agora depende de `web-service-dev` e `celery-worker-dev`
- Garante que as migrações sejam executadas antes dos serviços Celery

### 4. Script de Inicialização do Banco Corrigido
- Arquivo `database/init/init.sql` atualizado para detectar automaticamente o ambiente
- Suporte para ambos `mark_foot_db_dev` e `mark_foot_db_prod`

### 5. Script de Validação (`validate-celery-fix.py`)
- Verifica conexão com o banco
- Confirma existência da tabela `django_celery_beat_periodictask`
- Valida configuração do Celery

## Status da Validação

### ✅ Ambiente de Desenvolvimento
- [x] Containers funcionando estáveis
- [x] Celery Beat sem reinicializações
- [x] Tabelas do django_celery_beat criadas
- [x] Script de validação aprovado

### ✅ Ambiente de Produção
- [x] Docker Compose atualizado com as mesmas correções
- [x] Script de wait-for-db aplicado
- [x] Ordem de dependências corrigida
- [x] Comando do Gunicorn atualizado

## Comandos de Verificação

### Verificar status dos containers:
```bash
docker ps
```

### Verificar logs do Celery Beat:
```bash
docker logs mark_foot_celery_beat_dev --tail 20
```

### Executar validação:
```bash
docker exec mark_foot_web_dev python validate-celery-fix.py
```

### Verificar tabelas do Celery no banco:
```bash
docker exec mark_foot_mysql_dev mysql -u "mark_foot_user" -p"mark_foot_password" "mark_foot_db_dev" -e "SHOW TABLES LIKE '%celery%';"
```

## Próximos Passos
1. Testar em ambiente de staging/produção
2. Monitorar logs por 24h para garantir estabilidade
3. Criar alertas para monitoramento do Celery Beat
4. Documentar processo de rollback se necessário

## Data da Correção
**30 de agosto de 2025**

## Responsável
Sistema de correção automática aplicada via GitHub Copilot
