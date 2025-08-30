# Mark Foot - Script de Seeders para Desenvolvimento
# Este script facilita a execução dos seeders em ambiente Windows

param(
    [string]$Action = "full",
    [int]$Users = 20,
    [switch]$Reset,
    [switch]$Quick,
    [string[]]$Modules,
    [switch]$Help
)

function Show-Help {
    Write-Host "🌱 Mark Foot - Sistema de Seeders" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\run_seeders.ps1 [action] [options]"
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor Yellow
    Write-Host "  full      - Popula todos os módulos (padrão)"
    Write-Host "  quick     - Modo rápido com dados mínimos"  
    Write-Host "  users     - Apenas usuários de teste"
    Write-Host "  content   - Apenas conteúdo e categorias"
    Write-Host "  social    - Apenas recursos sociais"
    Write-Host "  reset     - Reseta e repopula tudo (CUIDADO!)"
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Users <n>       Número de usuários (padrão: 20)"
    Write-Host "  -Reset           Apaga dados antes de popular"
    Write-Host "  -Quick           Modo rápido para todos os comandos"
    Write-Host "  -Modules <list>  Módulos específicos: users,content,polls,social,etc"
    Write-Host "  -Help            Mostra esta ajuda"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Cyan
    Write-Host "  .\run_seeders.ps1"
    Write-Host "  .\run_seeders.ps1 quick"
    Write-Host "  .\run_seeders.ps1 reset -Reset"
    Write-Host "  .\run_seeders.ps1 full -Users 50"
    Write-Host "  .\run_seeders.ps1 -Modules users,content"
}

function Test-DockerEnvironment {
    Write-Host "🔍 Verificando ambiente Docker..." -ForegroundColor Blue
    
    $containers = docker ps --format "table {{.Names}}" | Where-Object { $_ -match "mark_foot.*dev" }
    
    if (-not $containers) {
        Write-Host "❌ Containers de desenvolvimento não estão rodando!" -ForegroundColor Red
        Write-Host "   Execute: docker-compose -f docker/docker-compose.dev.yml up -d" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "✅ Containers de desenvolvimento ativos" -ForegroundColor Green
    return $true
}

function Invoke-SeederCommand {
    param([string]$Command)
    
    Write-Host "🚀 Executando: $Command" -ForegroundColor Blue
    
    $result = docker exec mark_foot_web_dev python manage.py $Command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Comando executado com sucesso" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao executar comando" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
    
    return $LASTEXITCODE -eq 0
}

# Mostrar ajuda se solicitado
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "🌱 Mark Foot - Sistema de Seeders" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Verificar ambiente Docker
if (-not (Test-DockerEnvironment)) {
    exit 1
}

# Construir comando base
$baseCommand = "seed_dev_data"
$commandArgs = @()

# Processar ação
switch ($Action.ToLower()) {
    "full" {
        Write-Host "📦 Modo: Seeding completo" -ForegroundColor Cyan
        # Sem argumentos adicionais - usa padrões
    }
    "quick" {
        Write-Host "⚡ Modo: Seeding rápido" -ForegroundColor Cyan
        $commandArgs += "--quick"
    }
    "users" {
        Write-Host "👤 Modo: Apenas usuários" -ForegroundColor Cyan
        $commandArgs += "--modules", "users"
    }
    "content" {
        Write-Host "📝 Modo: Apenas conteúdo" -ForegroundColor Cyan
        $commandArgs += "--modules", "content"
    }
    "social" {
        Write-Host "👥 Modo: Apenas social" -ForegroundColor Cyan
        $commandArgs += "--modules", "social"
    }
    "reset" {
        Write-Host "🗑️  Modo: Reset completo" -ForegroundColor Red
        $commandArgs += "--reset"
        
        Write-Host "⚠️  ATENÇÃO: Isso apagará TODOS os dados!" -ForegroundColor Red
        $confirm = Read-Host "Tem certeza? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "❌ Operação cancelada" -ForegroundColor Yellow
            exit 0
        }
    }
    default {
        Write-Host "❌ Ação inválida: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

# Processar opções
if ($Reset) {
    $commandArgs += "--reset"
}

if ($Quick) {
    $commandArgs += "--quick"
}

if ($Users -ne 20) {
    $commandArgs += "--users-count", $Users
}

if ($Modules) {
    $commandArgs += "--modules"
    $commandArgs += $Modules -join ","
}

# Montar comando final
$finalCommand = $baseCommand
if ($commandArgs.Count -gt 0) {
    $finalCommand += " " + ($commandArgs -join " ")
}

Write-Host ""
Write-Host "⚙️  Configuração:" -ForegroundColor Yellow
Write-Host "   Usuários: $Users"
Write-Host "   Reset: $Reset"
Write-Host "   Modo rápido: $Quick"
if ($Modules) {
    Write-Host "   Módulos: $($Modules -join ', ')"
}
Write-Host ""

# Executar comando
$success = Invoke-SeederCommand $finalCommand

if ($success) {
    Write-Host ""
    Write-Host "🎉 Seeders executados com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Acesse sua aplicação:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000"
    Write-Host "   Backend:  http://localhost:8001"
    Write-Host "   Admin:    http://localhost:8001/admin"
    Write-Host ""
    Write-Host "👤 Login de teste:" -ForegroundColor Cyan
    Write-Host "   Usuário: admin"
    Write-Host "   Senha:   admin123"
} else {
    Write-Host ""
    Write-Host "❌ Erro ao executar seeders!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para mais detalhes" -ForegroundColor Yellow
}
