#!/bin/bash

# ==============================================================================
# Mark Foot - Script de Setup Simples para Desenvolvimento (Linux/Mac)
# ==============================================================================
# Uso: ./start-dev.sh
# ==============================================================================

set -e

RESET=false

show_help() {
    echo ""
    echo "===== MARK FOOT - SETUP DE DESENVOLVIMENTO ====="
    echo ""
    echo "USO:"
    echo "  ./start-dev.sh         # Inicia ambiente de desenvolvimento"
    echo "  ./start-dev.sh --reset # Reset completo (apaga dados e recria)"
    echo "  ./start-dev.sh --help  # Mostra esta ajuda"
    echo ""
    echo "O QUE ESTE SCRIPT FAZ:"
    echo "  1. Verifica se Docker esta rodando"
    echo "  2. Para containers antigos (se existirem)"
    echo "  3. Inicia todos os containers de desenvolvimento"
    echo "  4. Aguarda banco de dados ficar pronto"
    echo "  5. Aplica migrations (se necessario)"
    echo "  6. Popula dados de teste (se necessario)"
    echo "  7. Verifica dependencias do frontend"
    echo "  8. Mostra URLs de acesso"
    echo ""
}

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --reset)
            RESET=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "ERRO: Argumento desconhecido: $1"
            show_help
            exit 1
            ;;
    esac
done

echo ""
echo "===== MARK FOOT - INICIANDO AMBIENTE DE DESENVOLVIMENTO ====="
echo ""

# Verificar Docker
echo "[1/8] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker nao esta instalado!"
    exit 1
fi

if ! docker version &> /dev/null; then
    echo "ERRO: Docker nao esta rodando!"
    exit 1
fi

echo "OK: Docker esta funcionando"

# Verificar estrutura do projeto
if [ ! -f "docker/docker-compose.dev.yml" ]; then
    echo "ERRO: Execute este script na raiz do projeto Mark Foot"
    exit 1
fi

# Parar containers existentes
echo "[2/8] Parando containers existentes..."
docker-compose -f docker/docker-compose.dev.yml down &> /dev/null || true

# Reset se solicitado
if [ "$RESET" = true ]; then
    echo "[2.5/8] RESETANDO AMBIENTE COMPLETO..."
    echo "ATENCAO: Isso apagara todos os dados do banco!"
    read -p "Continuar? (s/N): " confirm
    if [[ ! "$confirm" =~ ^[sS]$ ]]; then
        echo "Cancelado pelo usuario"
        exit 0
    fi
    docker-compose -f docker/docker-compose.dev.yml down -v &> /dev/null || true
    echo "Ambiente resetado"
fi

# Iniciar containers
echo "[3/8] Iniciando containers..."
echo "Aguarde, pode demorar alguns minutos na primeira vez..."

if ! docker-compose -f docker/docker-compose.dev.yml up -d; then
    echo "ERRO ao iniciar containers"
    exit 1
fi

echo "OK: Containers iniciados"

# Aguardar banco de dados
echo "[4/8] Aguardando banco de dados..."
attempt=0
while [ $attempt -lt 30 ]; do
    attempt=$((attempt + 1))
    sleep 2
    if docker exec mark_foot_mysql_dev mysqladmin ping -h localhost -u root -proot_password &> /dev/null; then
        break
    fi
    echo -n "."
done

if [ $attempt -ge 30 ]; then
    echo ""
    echo "ERRO: Timeout aguardando banco de dados"
    exit 1
fi

echo ""
echo "OK: Banco de dados pronto"

# Aguardar web service
echo "[5/8] Aguardando web service..."
attempt=0
while [ $attempt -lt 20 ]; do
    attempt=$((attempt + 1))
    sleep 3
    if curl -s -f "http://localhost:8001/api/v1/" > /dev/null 2>&1; then
        break
    fi
    echo -n "."
done

if [ $attempt -ge 20 ]; then
    echo ""
    echo "ERRO: Web service nao esta respondendo"
    exit 1
fi

echo ""
echo "OK: Web service funcionando"

# Verificar migrations
echo "[6/8] Verificando migrations..."
if migrations_output=$(docker exec mark_foot_web_dev python manage.py showmigrations --plan 2>/dev/null); then
    unapplied=$(echo "$migrations_output" | grep "\[ \]" || true)
    if [ ! -z "$unapplied" ]; then
        echo "Aplicando migrations..."
        if docker exec mark_foot_web_dev python manage.py migrate &> /dev/null; then
            echo "OK: Migrations aplicadas"
        else
            echo "AVISO: Erro ao aplicar migrations"
        fi
    else
        echo "OK: Migrations ja aplicadas"
    fi
else
    echo "AVISO: Erro ao verificar migrations"
fi

# Verificar dados
echo "[7/8] Verificando dados no banco..."
if user_count=$(docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null); then
    if [ "$user_count" -gt 0 ] 2>/dev/null; then
        echo "OK: Banco possui dados ($user_count usuarios)"
    else
        echo "Populando dados de desenvolvimento..."
        docker exec mark_foot_web_dev python manage.py seed_dev_data --quick &> /dev/null || true
        echo "OK: Dados criados"
    fi
else
    echo "Populando dados de desenvolvimento..."
    docker exec mark_foot_web_dev python manage.py seed_dev_data --quick &> /dev/null || true
    echo "OK: Dados criados"
fi

# Verificar/criar superuser
if admin_exists=$(docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())" 2>/dev/null); then
    if [ "$admin_exists" != "True" ]; then
        echo "Criando superuser 'admin'..."
        docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@markfoot.com', 'admin123')" &> /dev/null || true
    fi
fi

# Verificar dependencias criticas do frontend
echo "[8/8] Verificando dependencias do frontend..."
critical_deps=("lodash-es" "vue" "vue-router" "pinia" "vuetify" "axios" "chart.js" "date-fns")
missing_deps=()

for dep in "${critical_deps[@]}"; do
    if ! docker exec mark_foot_frontend_dev test -d "/app/node_modules/$dep" &> /dev/null; then
        missing_deps+=("$dep")
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "Instalando dependencias faltantes do frontend..."
    for dep in "${missing_deps[@]}"; do
        docker exec mark_foot_frontend_dev npm install "$dep" --silent &> /dev/null || true
    done
    echo "Reiniciando container do frontend..."
    docker restart mark_foot_frontend_dev &> /dev/null || true
    sleep 3
    echo "OK: Dependencias do frontend corrigidas"
else
    echo "OK: Dependencias do frontend verificadas"
fi

# Resumo final
echo ""
echo "=============================================="
echo "    AMBIENTE PRONTO PARA DESENVOLVIMENTO!"
echo "=============================================="
echo ""

echo "CONTAINERS ATIVOS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(mark_foot.*dev|NAMES)"

echo ""
echo "ACESSE SUA APLICACAO:"
echo "  Frontend:     http://localhost:3000"
echo "  Backend API:  http://localhost:8001/api/v1/"
echo "  Django Admin: http://localhost:8001/admin/"

echo ""
echo "CREDENCIAIS:"
echo "  Usuario: admin"
echo "  Senha:   admin123"

echo ""
echo "COMANDOS UTEIS:"
echo "  Ver logs:    docker-compose -f docker/docker-compose.dev.yml logs -f"
echo "  Parar tudo:  docker-compose -f docker/docker-compose.dev.yml down"
echo "  Reset:       ./start-dev.sh --reset"

echo ""
echo "PRONTO! Voce pode comecar a desenvolver!"
echo ""
