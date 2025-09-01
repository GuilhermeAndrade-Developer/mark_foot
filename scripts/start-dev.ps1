# Mark Foot - Script de Desenvolvimento Automatizado
# Executa containers, aplica migrations e popula dados automaticamente

param(
    [switch]$Reset,
    [switch]$Help
)

function Show-Help {
    Write-Host "===== MARK FOOT - SETUP DE DESENVOLVIMENTO ====="
    Write-Host ""
    Write-Host "USO:"
    Write-Host "  .\start-dev.ps1         # Inicia ambiente"
    Write-Host "  .\start-dev.ps1 -Reset  # Reset completo"
    Write-Host "  .\start-dev.ps1 -Help   # Mostra ajuda"
    Write-Host ""
}

function Execute-Seeders {
    Write-Host ""
    Write-Host "Populando banco de dados com seeders..." -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    
    # Detecta automaticamente todos os seeders
    Write-Host "Detectando seeders automaticamente..."
    $seederFiles = Get-ChildItem -Path "database/seeders" -Filter "seed_*.py" | Sort-Object Name
    
    if ($seederFiles.Count -eq 0) {
        Write-Host "ERRO: Nenhum seeder encontrado em database/seeders!" -ForegroundColor Red
        return
    }
    
    $seeders = $seederFiles | ForEach-Object { $_.Name }
    Write-Host "Encontrados $($seeders.Count) seeders: $($seeders -join ', ')" -ForegroundColor Gray
    
    $totalSeeders = $seeders.Count
    $currentSeeder = 0
    $successCount = 0
    $failureCount = 0
    
    $startTime = Get-Date
    
    foreach ($seeder in $seeders) {
        $currentSeeder++
        $percentage = [Math]::Round(($currentSeeder / $totalSeeders) * 100, 1)
        
        Write-Host ""
        Write-Host "[$currentSeeder/$totalSeeders] ($percentage%) Executando $seeder..." -ForegroundColor Yellow
        Write-Host "  -> " -NoNewline
        
        $seederStartTime = Get-Date
        
        # Comando para executar o seeder
        $command = "import sys; sys.path.append('/app'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mark_foot_backend.settings'); import django; django.setup(); exec(open('/database/seeders/$seeder').read())"
        
        # Executar com job para controle de tempo
        $job = Start-Job -ScriptBlock {
            param($cmd, $seederFile)
            $result = docker exec mark_foot_web_dev python -c $cmd 2>&1
            return $result
        } -ArgumentList $command, $seeder
        
        # Aguardar com timer visual
        $timeout = 60
        $elapsed = 0
        while ($job.State -eq "Running" -and $elapsed -lt $timeout) {
            Start-Sleep 1
            $elapsed++
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
        
        # Verificar resultado
        $completed = $false
        if ($job.State -eq "Completed") {
            $output = Receive-Job $job
            $completed = $true
        } else {
            Stop-Job $job
            $output = "Timeout"
        }
        
        Remove-Job $job -Force
        
        $seederEndTime = Get-Date
        $seederDuration = ($seederEndTime - $seederStartTime).TotalSeconds
        
        if ($completed) {
            Write-Host " OK" -ForegroundColor Green
            Write-Host "     Tempo: $([Math]::Round($seederDuration, 1))s" -ForegroundColor Gray
            $successCount++
        } else {
            Write-Host " FALHOU" -ForegroundColor Red
            Write-Host "     Tempo: $([Math]::Round($seederDuration, 1))s (timeout)" -ForegroundColor Gray
            $failureCount++
        }
    }
    
    $endTime = Get-Date
    $totalDuration = ($endTime - $startTime).TotalSeconds
    
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "SEEDERS CONCLUIDOS!" -ForegroundColor Green
    Write-Host "   Sucessos: $successCount" -ForegroundColor Green
    Write-Host "   Falhas: $failureCount" -ForegroundColor Yellow
    Write-Host "   Tempo total: $([Math]::Round($totalDuration, 1))s" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar dados finais
    Write-Host "Verificando dados populados..."
    
    $userResult = docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>$null
    $teamResult = docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Team; print(Team.objects.count())" 2>$null
    $playerResult = docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Player; print(Player.objects.count())" 2>$null
    $planResult = docker exec mark_foot_web_dev python manage.py shell -c "from billing.models import SubscriptionPlan; print(SubscriptionPlan.objects.count())" 2>$null
    
    Write-Host "   Usuarios: $userResult" -ForegroundColor White
    Write-Host "   Times: $teamResult" -ForegroundColor White
    Write-Host "   Jogadores: $playerResult" -ForegroundColor White
    Write-Host "   Planos: $planResult" -ForegroundColor White
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
Write-Host "[1/8] Verificando Docker..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: Docker nao esta instalado!" -ForegroundColor Red
    exit 1
}

try {
    docker version | Out-Null
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
Write-Host "[2/8] Parando containers existentes..."
docker-compose -f docker/docker-compose.dev.yml down 2>$null | Out-Null

# Reset se solicitado
if ($Reset) {
    Write-Host "[2.5/8] RESETANDO AMBIENTE COMPLETO..."
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
Write-Host "[3/8] Iniciando containers..."
Write-Host "Aguarde, pode demorar alguns minutos na primeira vez..."

$result = docker-compose -f docker/docker-compose.dev.yml up -d 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao iniciar containers:" -ForegroundColor Red
    Write-Host $result
    exit 1
}

Write-Host "OK: Containers iniciados"

# Aguardar banco de dados
Write-Host "[4/8] Aguardando banco de dados..."
$attempt = 0
do {
    $attempt++
    Start-Sleep 2
    docker exec mark_foot_mysql_dev mysqladmin ping -h localhost -u root -proot_password 2>$null | Out-Null
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
Write-Host "[5/8] Aguardando web service..."
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
} while ($attempt -lt 30)

if ($attempt -ge 30) {
    Write-Host ""
    Write-Host "ERRO: Web service nao esta respondendo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "OK: Web service funcionando"

# Verificar migrations
Write-Host "[6/8] Verificando migrations..."
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
Write-Host "[7/8] Verificando dados no banco..."

# Verificar se temos usuários
$userCountResult = docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>$null
$userCount = 0
if ($userCountResult -and $userCountResult -match '^\d+$') {
    $userCount = [int]$userCountResult
}

if ($userCount -gt 5) {
    Write-Host "OK: Banco possui dados ($userCount usuarios)"
    
    # Verificar se temos dados completos nas principais tabelas
    $teamCountResult = docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Team; print(Team.objects.count())" 2>$null
    $playerCountResult = docker exec mark_foot_web_dev python manage.py shell -c "from core.models import Player; print(Player.objects.count())" 2>$null
    $subscriptionCountResult = docker exec mark_foot_web_dev python manage.py shell -c "from billing.models import SubscriptionPlan; print(SubscriptionPlan.objects.count())" 2>$null
    
    $teamCount = if ($teamCountResult -and $teamCountResult -match '^\d+$') { [int]$teamCountResult } else { 0 }
    $playerCount = if ($playerCountResult -and $playerCountResult -match '^\d+$') { [int]$playerCountResult } else { 0 }
    $subscriptionCount = if ($subscriptionCountResult -and $subscriptionCountResult -match '^\d+$') { [int]$subscriptionCountResult } else { 0 }
    
    if ($teamCount -eq 0 -or $playerCount -eq 0 -or $subscriptionCount -eq 0) {
        Write-Host "Dados basicos incompletos, executando todos os seeders..."
        Execute-Seeders
    } else {
        Write-Host "Dados basicos OK: $teamCount teams, $playerCount players, $subscriptionCount plans"
    }
} else {
    Write-Host "Banco vazio ou com poucos dados, executando todos os seeders..."
    
    # Criar superuser admin se não existir
    Write-Host "  -> Criando usuario admin..."
    $createAdminCmd = 'from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@markfoot.com", "admin123") if not User.objects.filter(username="admin").exists() else None'
    docker exec mark_foot_web_dev python manage.py shell -c $createAdminCmd 2>&1 | Out-Null
    
    Execute-Seeders
}

# Verificar/criar superuser
$adminExistsResult = docker exec mark_foot_web_dev python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())" 2>$null

if ($adminExistsResult -ne "True") {
    Write-Host "Criando superuser 'admin'..."
    $createAdminCmd2 = 'from django.contrib.auth.models import User; User.objects.create_superuser("admin", "admin@markfoot.com", "admin123")'
    docker exec mark_foot_web_dev python manage.py shell -c $createAdminCmd2 2>$null | Out-Null
}

# Verificar dependências críticas do frontend
Write-Host "[8/8] Verificando dependencias do frontend..."
$criticalDeps = @("lodash-es", "vue", "vue-router", "pinia", "vuetify", "axios", "chart.js", "date-fns")
$missingDeps = @()

foreach ($dep in $criticalDeps) {
    docker exec mark_foot_frontend_dev test -d "/app/node_modules/$dep" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "Instalando dependencias faltantes do frontend..."
    foreach ($dep in $missingDeps) {
        docker exec mark_foot_frontend_dev npm install $dep --silent 2>$null | Out-Null
    }
    Write-Host "Reiniciando container do frontend..."
    docker restart mark_foot_frontend_dev 2>$null | Out-Null
    Start-Sleep 3
    Write-Host "OK: Dependencias do frontend corrigidas"
} else {
    Write-Host "OK: Dependencias do frontend verificadas"
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
