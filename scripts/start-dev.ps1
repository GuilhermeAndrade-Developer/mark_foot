# ==============================================================================
# Mark Foot - Script de Setup Simples para Desenvolvimento (Windows)
# ==============================================================================
# Uso: .\start-dev.ps1
# ==============================================================================

param(
    [switch]$Reset,
    [switch]$Help
)

function Show-Help {
    Write-Host ""
    Write-Host "===== MARK FOOT - SETUP DE DESENVOLVIMENTO ====="
    Write-Host ""
    Write-Host "USO:"
    Write-Host "  .\start-dev.ps1         # Inicia ambiente de desenvolvimento"
    Write-Host "  .\start-dev.ps1 -Reset  # Reset completo (apaga dados e recria)"
    Write-Host "  .\start-dev.ps1 -Help   # Mostra esta ajuda"
    Write-Host ""
    Write-Host "O QUE ESTE SCRIPT FAZ:"
    Write-Host "  1. Verifica se Docker esta rodando"
    Write-Host "  2. Para containers antigos (se existirem)"
    Write-Host "  3. Inicia todos os containers de desenvolvimento"
    Write-Host "  4. Aguarda banco de dados ficar pronto"
    Write-Host "  5. Aplica migrations (se necessario)"
    Write-Host "  6. Popula dados de teste (se necessario)"
    Write-Host "  7. Mostra URLs de acesso"
    Write-Host ""
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Host "===== MARK FOOT - INICIANDO AMBIENTE DE DESENVOLVIMENTO ====="
Write-Host ""

# Verificar Docker
Write-Host "[1/7] Verificando Docker..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Docker nao esta instalado!" -ForegroundColor Red
    exit 1
}

try {
    $null = docker version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Docker esta funcionando"

# Verificar estrutura do projeto
if (-not (Test-Path "docker/docker-compose.dev.yml")) {
    Write-Host "ERRO: Execute este script na raiz do projeto Mark Foot" -ForegroundColor Red
    exit 1
}

# Parar containers existentes
Write-Host "[2/7] Parando containers existentes..."
docker-compose -f docker/docker-compose.dev.yml down 2>$null | Out-Null

# Reset se solicitado
if ($Reset) {
    Write-Host "[2.5/7] RESETANDO AMBIENTE COMPLETO..."
    Write-Host "ATENCAO: Isso apagara todos os dados do banco!"
    $confirm = Read-Host "Continuar? (s/N)"
    if ($confirm -ne "s" -and $confirm -ne "S") {
        Write-Host "Cancelado pelo usuario"
        exit 0
    }
    docker-compose -f docker/docker-compose.dev.yml down -v 2>$null | Out-Null
    Write-Host "Ambiente resetado"
}

# Iniciar containers
Write-Host "[3/7] Iniciando containers..."
Write-Host "Aguarde, pode demorar alguns minutos na primeira vez..."

$result = docker-compose -f docker/docker-compose.dev.yml up -d 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao iniciar containers:" -ForegroundColor Red
    Write-Host $result
    exit 1
}

Write-Host "OK: Containers iniciados"

# Aguardar banco de dados
Write-Host "[4/7] Aguardando banco de dados..."
$attempt = 0
do {
    $attempt++
    Start-Sleep 2
    $dbStatus = docker exec mark_foot_mysql_dev mysqladmin ping -h localhost -u root -proot_password 2>$null
    if ($LASTEXITCODE -eq 0) {
        break
    }
    Write-Host "." -NoNewline
} while ($attempt -lt 30)

if ($attempt -ge 30) {
    Write-Host ""
    Write-Host "ERRO: Timeout aguardando banco de dados" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "OK: Banco de dados pronto"

# Aguardar web service
Write-Host "[5/7] Aguardando web service..."
$attempt = 0
do {
    $attempt++
    Start-Sleep 3
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            break
        }
    } catch {
        # Continuar tentando
    }
    Write-Host "." -NoNewline
} while ($attempt -lt 20)

if ($attempt -ge 20) {
    Write-Host ""
    Write-Host "ERRO: Web service nao esta respondendo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "OK: Web service funcionando"

# Verificar migrations
Write-Host "[6/7] Verificando migrations..."
$migrations = docker exec mark_foot_web_dev python manage.py showmigrations --plan 2>$null
if ($LASTEXITCODE -eq 0) {
    $unapplied = $migrations | Select-String "\[ \]"
    if ($unapplied) {
        Write-Host "Aplicando migrations..."
        docker exec mark_foot_web_dev python manage.py migrate 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Migrations aplicadas"
        } else {
            Write-Host "AVISO: Erro ao aplicar migrations" -ForegroundColor Yellow
        }
    } else {
        Write-Host "OK: Migrations ja aplicadas"
    }
} else {
    Write-Host "AVISO: Erro ao verificar migrations" -ForegroundColor Yellow
}

# Verificar dados
Write-Host "[7/7] Verificando dados no banco..."
$userCount = docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>$null

if ($LASTEXITCODE -eq 0 -and [int]$userCount -gt 0) {
    Write-Host "OK: Banco possui dados ($userCount usuarios)"
} else {
    Write-Host "Populando dados de desenvolvimento..."
    docker exec mark_foot_web_dev python manage.py seed_dev_data --quick 2>&1 | Out-Null
    Write-Host "OK: Dados criados"
}

# Verificar/criar superuser
$adminExists = docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())" 2>$null

if ($adminExists -ne "True") {
    Write-Host "Criando superuser 'admin'..."
    docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@markfoot.com', 'admin123')" 2>$null | Out-Null
}

# Resumo final
Write-Host ""
Write-Host "=============================================="
Write-Host "    AMBIENTE PRONTO PARA DESENVOLVIMENTO!"
Write-Host "=============================================="
Write-Host ""

Write-Host "CONTAINERS ATIVOS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Where-Object { $_ -match "mark_foot.*dev|NAMES" }

Write-Host ""
Write-Host "ACESSE SUA APLICACAO:"
Write-Host "  Frontend:     http://localhost:3000"
Write-Host "  Backend API:  http://localhost:8001/api/v1/"
Write-Host "  Django Admin: http://localhost:8001/admin/"

Write-Host ""
Write-Host "CREDENCIAIS:"
Write-Host "  Usuario: admin"
Write-Host "  Senha:   admin123"

Write-Host ""
Write-Host "COMANDOS UTEIS:"
Write-Host "  Ver logs:    docker-compose -f docker/docker-compose.dev.yml logs -f"
Write-Host "  Parar tudo:  docker-compose -f docker/docker-compose.dev.yml down"
Write-Host "  Reset:       .\start-dev.ps1 -Reset"

Write-Host ""
Write-Host "PRONTO! Voce pode comecar a desenvolver!" -ForegroundColor Green
Write-Host ""
