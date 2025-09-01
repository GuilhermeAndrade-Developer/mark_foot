#!/bin/bash
# Mark Foot - Script de Desenvolvimento Automatizado (Linux/macOS)
# Executa containers, aplica migrations e popula dados automaticamente

set -e

RESET=false
HELP=false

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --reset)
            RESET=true
            shift
            ;;
        --help)
            HELP=true
            shift
            ;;
        *)
            echo "Argumento desconhecido: $1"
            exit 1
            ;;
    esac
done

show_help() {
    echo "===== MARK FOOT - SETUP DE DESENVOLVIMENTO ====="
    echo ""
    echo "USO:"
    echo "  ./start-dev.sh         # Inicia ambiente"
    echo "  ./start-dev.sh --reset # Reset completo"
    echo "  ./start-dev.sh --help  # Mostra ajuda"
    echo ""
}

execute_seeders() {
    echo ""
    echo -e "\033[36mPopulando banco de dados com seeders...\033[0m"
    echo -e "\033[36m=========================================\033[0m"
    
    # Detecta automaticamente todos os seeders
    echo "Detectando seeders automaticamente..."
    
    if [ ! -d "database/seeders" ]; then
        echo -e "\033[31mERRO: Diretório database/seeders não encontrado!\033[0m"
        return 1
    fi
    
    seeders=($(ls database/seeders/seed_*.py 2>/dev/null | sort | xargs -n1 basename))
    
    if [ ${#seeders[@]} -eq 0 ]; then
        echo -e "\033[31mERRO: Nenhum seeder encontrado em database/seeders!\033[0m"
        return 1
    fi
    
    echo -e "\033[37mEncontrados ${#seeders[@]} seeders: ${seeders[*]}\033[0m"

    
    total_seeders=${#seeders[@]}
    current_seeder=0
    success_count=0
    failure_count=0
    
    start_time=$(date +%s)
    
    for seeder in "${seeders[@]}"; do
        current_seeder=$((current_seeder + 1))
        percentage=$(echo "scale=1; ($current_seeder * 100) / $total_seeders" | bc -l)
        
        echo ""
        echo -e "\033[33m[$current_seeder/$total_seeders] ($percentage%) Executando $seeder...\033[0m"
        echo -n "  -> "
        
        seeder_start_time=$(date +%s)
        
        # Comando para executar o seeder
        command="import sys; sys.path.append('/app'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings'); import django; django.setup(); exec(open('/database/seeders/$seeder').read())"
        
        # Executar com timeout
        if timeout 60 docker exec mark_foot_web_dev python -c "$command" >/dev/null 2>&1; then
            seeder_end_time=$(date +%s)
            seeder_duration=$((seeder_end_time - seeder_start_time))
            echo -e " \033[32mOK\033[0m"
            echo -e "     \033[37mTempo: ${seeder_duration}s\033[0m"
            success_count=$((success_count + 1))
        else
            seeder_end_time=$(date +%s)
            seeder_duration=$((seeder_end_time - seeder_start_time))
            echo -e " \033[31mFALHOU\033[0m"
            echo -e "     \033[37mTempo: ${seeder_duration}s (timeout ou erro)\033[0m"
            failure_count=$((failure_count + 1))
        fi
    done
    
    end_time=$(date +%s)
    total_duration=$((end_time - start_time))
    
    echo ""
    echo -e "\033[36m=========================================\033[0m"
    echo -e "\033[32mSEEDERS CONCLUIDOS!\033[0m"
    echo -e "   \033[32mSucessos: $success_count\033[0m"
    echo -e "   \033[33mFalhas: $failure_count\033[0m"
    echo -e "   \033[36mTempo total: ${total_duration}s\033[0m"
    echo ""
    
    # Verificar dados finais
    echo "Verificando dados populados..."
    
    user_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null || echo "0")
    team_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Team; print(Team.objects.count())" 2>/dev/null || echo "0")
    player_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Player; print(Player.objects.count())" 2>/dev/null || echo "0")
    plan_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from billing.models import SubscriptionPlan; print(SubscriptionPlan.objects.count())" 2>/dev/null || echo "0")
    
    echo -e "   \033[37mUsuarios: $user_result\033[0m"
    echo -e "   \033[37mTimes: $team_result\033[0m"
    echo -e "   \033[37mJogadores: $player_result\033[0m"
    echo -e "   \033[37mPlanos: $plan_result\033[0m"
    echo ""
}

if [ "$HELP" = true ]; then
    show_help
    exit 0
fi

echo ""
echo "===== MARK FOOT - INICIANDO AMBIENTE DE DESENVOLVIMENTO ====="
echo ""

# Verificar Docker
echo "[1/8] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "\033[31mERRO: Docker não está instalado!\033[0m"
    exit 1
fi

if ! docker version &> /dev/null; then
    echo -e "\033[31mERRO: Docker não está rodando!\033[0m"
    exit 1
fi

echo "OK: Docker está funcionando"

# Verificar estrutura do projeto
if [ ! -f "docker/docker-compose.dev.yml" ]; then
    echo -e "\033[31mERRO: Execute este script na raiz do projeto Mark Foot\033[0m"
    exit 1
fi

# Parar containers existentes
echo "[2/8] Parando containers existentes..."
docker-compose -f docker/docker-compose.dev.yml down &>/dev/null || true

# Reset se solicitado
if [ "$RESET" = true ]; then
    echo "[2.5/8] RESETANDO AMBIENTE COMPLETO..."
    echo "ATENÇÃO: Isso apagará todos os dados do banco!"
    read -p "Continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Cancelado pelo usuário"
        exit 0
    fi
    docker-compose -f docker/docker-compose.dev.yml down -v &>/dev/null || true
    echo "Ambiente resetado"
fi

# Iniciar containers
echo "[3/8] Iniciando containers..."
echo "Aguarde, pode demorar alguns minutos na primeira vez..."

if ! docker-compose -f docker/docker-compose.dev.yml up -d; then
    echo -e "\033[31mERRO ao iniciar containers\033[0m"
    exit 1
fi

echo "OK: Containers iniciados"

# Aguardar banco de dados
echo "[4/8] Aguardando banco de dados..."
attempt=0
while [ $attempt -lt 30 ]; do
    attempt=$((attempt + 1))
    sleep 2
    if docker exec mark_foot_mysql_dev mysqladmin ping -h localhost -u root -proot_password &>/dev/null; then
        break
    fi
    echo -n "."
done

if [ $attempt -ge 30 ]; then
    echo ""
    echo -e "\033[31mERRO: Timeout aguardando banco de dados\033[0m"
    exit 1
fi

echo ""
echo "OK: Banco de dados pronto"

# Aguardar web service
echo "[5/8] Aguardando web service..."
attempt=0
while [ $attempt -lt 30 ]; do
    attempt=$((attempt + 1))
    sleep 3
    if curl -s http://localhost:8001/api/v1/ &>/dev/null; then
        break
    fi
    echo -n "."
done

if [ $attempt -ge 30 ]; then
    echo ""
    echo -e "\033[31mERRO: Web service não está respondendo\033[0m"
    exit 1
fi

echo ""
echo "OK: Web service funcionando"

# Verificar migrations
echo "[6/8] Verificando migrations..."
if migrations=$(docker exec mark_foot_web_dev python manage.py showmigrations --plan 2>/dev/null); then
    if echo "$migrations" | grep -q "\[ \]"; then
        echo "Aplicando migrations..."
        if docker exec mark_foot_web_dev python manage.py migrate &>/dev/null; then
            echo "OK: Migrations aplicadas"
        else
            echo -e "\033[33mAVISO: Erro ao aplicar migrations\033[0m"
        fi
    else
        echo "OK: Migrations já aplicadas"
    fi
else
    echo -e "\033[33mAVISO: Erro ao verificar migrations\033[0m"
fi

# Verificar dados
echo "[7/8] Verificando dados no banco..."

# Verificar se temos usuários
user_count_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null || echo "0")
user_count=${user_count_result//[^0-9]/}

if [ "$user_count" -gt 5 ] 2>/dev/null; then
    echo "OK: Banco possui dados ($user_count usuarios)"
    
    # Verificar se temos dados completos nas principais tabelas
    team_count_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Team; print(Team.objects.count())" 2>/dev/null || echo "0")
    player_count_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Player; print(Player.objects.count())" 2>/dev/null || echo "0")
    subscription_count_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from billing.models import SubscriptionPlan; print(SubscriptionPlan.objects.count())" 2>/dev/null || echo "0")
    
    team_count=${team_count_result//[^0-9]/}
    player_count=${player_count_result//[^0-9]/}
    subscription_count=${subscription_count_result//[^0-9]/}
    
    if [ "$team_count" -eq 0 ] || [ "$player_count" -eq 0 ] || [ "$subscription_count" -eq 0 ] 2>/dev/null; then
        echo "Dados básicos incompletos, executando todos os seeders..."
        execute_seeders
    else
        echo "Dados básicos OK: $team_count teams, $player_count players, $subscription_count plans"
    fi
else
    echo "Banco vazio ou com poucos dados, executando todos os seeders..."
    
    # Criar superuser admin se não existir
    echo "  -> Criando usuario admin..."
    create_admin_cmd='from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@markfoot.com", "admin123") if not User.objects.filter(username="admin").exists() else None'
    docker exec mark_foot_web_dev python manage.py shell -c "$create_admin_cmd" &>/dev/null || true
    
    execute_seeders
fi

# Verificar/criar superuser
admin_exists_result=$(docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())" 2>/dev/null || echo "False")

if [ "$admin_exists_result" != "True" ]; then
    echo "Criando superuser 'admin'..."
    create_admin_cmd2='from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@markfoot.com", "admin123")'
    docker exec mark_foot_web_dev python manage.py shell -c "$create_admin_cmd2" &>/dev/null || true
fi

# Verificar dependências críticas do frontend
echo "[8/8] Verificando dependencias do frontend..."
critical_deps=("lodash-es" "vue" "vue-router" "pinia" "vuetify" "axios" "chart.js" "date-fns")
missing_deps=()

for dep in "${critical_deps[@]}"; do
    if ! docker exec mark_foot_frontend_dev test -d "/app/node_modules/$dep" &>/dev/null; then
        missing_deps+=("$dep")
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "Instalando dependencias faltantes do frontend..."
    for dep in "${missing_deps[@]}"; do
        docker exec mark_foot_frontend_dev npm install "$dep" --silent &>/dev/null || true
    done
    echo "Reiniciando container do frontend..."
    docker restart mark_foot_frontend_dev &>/dev/null || true
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
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "mark_foot.*dev|NAMES" || true

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
echo -e "\033[32mPRONTO! Voce pode comecar a desenvolver!\033[0m"
echo ""
