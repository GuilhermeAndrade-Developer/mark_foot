# Test Runner Script for Mark Foot Test Service (PowerShell)
# Usage: .\run_tests.ps1 [-TestType <type>] [-NoCoverage] [-Parallel] [-Quiet]

param(
    [string]$TestType = "all",
    [switch]$NoCoverage,
    [switch]$Parallel,
    [switch]$Quiet,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\run_tests.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -TestType <TYPE>   Test type: all, unit, integration, auth, api (default: all)"
    Write-Host "  -NoCoverage        Disable coverage reporting"
    Write-Host "  -Parallel          Run tests in parallel"
    Write-Host "  -Quiet             Reduce output verbosity"
    Write-Host "  -Help              Show this help message"
    exit 0
}

# Build pytest command
$PytestCmd = "python -m pytest"

# Add verbosity
if (-not $Quiet) {
    $PytestCmd += " -v"
}

# Add coverage
if (-not $NoCoverage) {
    $PytestCmd += " --cov=. --cov-report=html --cov-report=term-missing"
}

# Add parallel execution
if ($Parallel) {
    $PytestCmd += " -n auto"
}

# Add test type filter
switch ($TestType) {
    "unit" {
        $PytestCmd += " -m unit unit/"
    }
    "integration" {
        $PytestCmd += " -m integration integration/"
    }
    "auth" {
        $PytestCmd += " -m auth auth/"
    }
    "api" {
        $PytestCmd += " -m api"
    }
    "gamification" {
        $PytestCmd += " -m gamification unit/gamification/"
    }
    "social" {
        $PytestCmd += " -m social unit/social/"
    }
    "data" {
        $PytestCmd += " -m data data/"
    }
    "all" {
        # Run all tests
    }
    default {
        Write-Error "Unknown test type: $TestType"
        Write-Host "Valid types: all, unit, integration, auth, api, gamification, social, data"
        exit 1
    }
}

Write-Host "🧪 Running Mark Foot Tests" -ForegroundColor Green
Write-Host "Test Type: $TestType"
Write-Host "Coverage: $(-not $NoCoverage)"
Write-Host "Parallel: $Parallel"
Write-Host "Command: $PytestCmd"
Write-Host ""

# Set Django settings
$env:DJANGO_SETTINGS_MODULE = "test_settings"

# Run tests
try {
    Invoke-Expression $PytestCmd
    Write-Host ""
    Write-Host "✅ Tests completed!" -ForegroundColor Green
    
    if (-not $NoCoverage) {
        Write-Host "📊 Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
    }
}
catch {
    Write-Error "❌ Tests failed!"
    exit 1
}
