#!/bin/bash

# Mark Foot - Script de Seeders para Desenvolvimento
# Este script facilita a execução dos seeders em ambiente Unix/Linux/Mac

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Valores padrão
ACTION="full"
USERS=20
RESET=false
QUICK=false
MODULES=""

show_help() {
    echo -e "${GREEN}🌱 Mark Foot - Sistema de Seeders${NC}"
    echo ""
    echo -e "${YELLOW}USAGE:${NC}"
    echo "  ./run_seeders.sh [action] [options]"
    echo ""
    echo -e "${YELLOW}ACTIONS:${NC}"
    echo "  full      - Popula todos os módulos (padrão)"
    echo "  quick     - Modo rápido com dados mínimos"  
    echo "  users     - Apenas usuários de teste"
    echo "  content   - Apenas conteúdo e categorias"
    echo "  social    - Apenas recursos sociais"
    echo "  reset     - Reseta e repopula tudo (CUIDADO!)"
    echo ""
    echo -e "${YELLOW}OPTIONS:${NC}"
    echo "  --users <n>       Número de usuários (padrão: 20)"
    echo "  --reset           Apaga dados antes de popular"
    echo "  --quick           Modo rápido para todos os comandos"
    echo "  --modules <list>  Módulos específicos: users,content,polls,social,etc"
    echo "  --help            Mostra esta ajuda"
    echo ""
    echo -e "${CYAN}EXAMPLES:${NC}"
    echo "  ./run_seeders.sh"
    echo "  ./run_seeders.sh quick"
    echo "  ./run_seeders.sh reset --reset"
    echo "  ./run_seeders.sh full --users 50"
    echo "  ./run_seeders.sh --modules users,content"
}

test_docker_environment() {
    echo -e "${BLUE}🔍 Verificando ambiente Docker...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker não está instalado!${NC}"
        return 1
    fi
    
    local containers=$(docker ps --format "{{.Names}}" | grep "mark_foot.*dev" || true)
    
    if [ -z "$containers" ]; then
        echo -e "${RED}❌ Containers de desenvolvimento não estão rodando!${NC}"
        echo -e "${YELLOW}   Execute: docker-compose -f docker/docker-compose.dev.yml up -d${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Containers de desenvolvimento ativos${NC}"
    return 0
}

invoke_seeder_command() {
    local command="$1"
    echo -e "${BLUE}🚀 Executando: $command${NC}"
    
    if docker exec mark_foot_web_dev python manage.py $command; then
        echo -e "${GREEN}✅ Comando executado com sucesso${NC}"
        return 0
    else
        echo -e "${RED}❌ Erro ao executar comando${NC}"
        return 1
    fi
}

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --users)
            USERS="$2"
            shift 2
            ;;
        --reset)
            RESET=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --modules)
            MODULES="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$ACTION" || "$ACTION" == "full" ]]; then
                ACTION="$1"
            fi
            shift
            ;;
    esac
done

echo -e "${GREEN}🌱 Mark Foot - Sistema de Seeders${NC}"
echo "=================================="

# Verificar ambiente Docker
if ! test_docker_environment; then
    exit 1
fi

# Construir comando base
base_command="seed_dev_data"
command_args=""

# Processar ação
case "${ACTION,,}" in
    "full")
        echo -e "${CYAN}📦 Modo: Seeding completo${NC}"
        ;;
    "quick")
        echo -e "${CYAN}⚡ Modo: Seeding rápido${NC}"
        command_args="$command_args --quick"
        ;;
    "users")
        echo -e "${CYAN}👤 Modo: Apenas usuários${NC}"
        command_args="$command_args --modules users"
        ;;
    "content")
        echo -e "${CYAN}📝 Modo: Apenas conteúdo${NC}"
        command_args="$command_args --modules content"
        ;;
    "social")
        echo -e "${CYAN}👥 Modo: Apenas social${NC}"
        command_args="$command_args --modules social"
        ;;
    "reset")
        echo -e "${RED}🗑️  Modo: Reset completo${NC}"
        command_args="$command_args --reset"
        
        echo -e "${RED}⚠️  ATENÇÃO: Isso apagará TODOS os dados!${NC}"
        read -p "Tem certeza? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[yY]$ ]]; then
            echo -e "${YELLOW}❌ Operação cancelada${NC}"
            exit 0
        fi
        ;;
    *)
        echo -e "${RED}❌ Ação inválida: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac

# Processar opções
if [ "$RESET" = true ]; then
    command_args="$command_args --reset"
fi

if [ "$QUICK" = true ]; then
    command_args="$command_args --quick"
fi

if [ "$USERS" != "20" ]; then
    command_args="$command_args --users-count $USERS"
fi

if [ ! -z "$MODULES" ]; then
    command_args="$command_args --modules $MODULES"
fi

# Montar comando final
final_command="$base_command$command_args"

echo ""
echo -e "${YELLOW}⚙️  Configuração:${NC}"
echo "   Usuários: $USERS"
echo "   Reset: $RESET"
echo "   Modo rápido: $QUICK"
if [ ! -z "$MODULES" ]; then
    echo "   Módulos: $MODULES"
fi
echo ""

# Executar comando
if invoke_seeder_command "$final_command"; then
    echo ""
    echo -e "${GREEN}🎉 Seeders executados com sucesso!${NC}"
    echo ""
    echo -e "${CYAN}🔗 Acesse sua aplicação:${NC}"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8001"
    echo "   Admin:    http://localhost:8001/admin"
    echo ""
    echo -e "${CYAN}👤 Login de teste:${NC}"
    echo "   Usuário: admin"
    echo "   Senha:   admin123"
else
    echo ""
    echo -e "${RED}❌ Erro ao executar seeders!${NC}"
    echo -e "${YELLOW}   Verifique os logs acima para mais detalhes${NC}"
    exit 1
fi
