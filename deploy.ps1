# Script de Deploy Automático para Fly.io
# Execute: .\deploy.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   🚀 DEPLOY GALERA VOLEI - FLY.IO" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar se flyctl está instalado
Write-Host "🔍 Verificando flyctl..." -ForegroundColor Yellow
if (!(Get-Command flyctl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ flyctl não encontrado!" -ForegroundColor Red
    Write-Host "   Instale com: pwsh -Command 'iwr https://fly.io/install.ps1 -useb | iex'" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ flyctl encontrado`n" -ForegroundColor Green

# Verificar login
Write-Host "🔍 Verificando autenticação..." -ForegroundColor Yellow
$authCheck = flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Não autenticado!" -ForegroundColor Red
    Write-Host "   Execute: flyctl auth login`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Autenticado como: $authCheck`n" -ForegroundColor Green

# Verificar se app existe
Write-Host "🔍 Verificando se app existe..." -ForegroundColor Yellow
flyctl status -a galera-volei 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  App não existe, criando...`n" -ForegroundColor Yellow
    
    Write-Host "📝 Criando aplicação no Fly.io..." -ForegroundColor Cyan
    flyctl launch --name galera-volei --region gru --no-deploy --copy-config --yes
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao criar app!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ App criada com sucesso!`n" -ForegroundColor Green
} else {
    Write-Host "✅ App já existe`n" -ForegroundColor Green
}

# Deploy
Write-Host "🚀 Iniciando deploy..." -ForegroundColor Cyan
Write-Host "   Isso pode levar alguns minutos...`n" -ForegroundColor Gray

flyctl deploy --remote-only

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "   ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor White -BackgroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Host "📊 Informações da aplicação:" -ForegroundColor Cyan
    flyctl info
    
    Write-Host "`n🌐 URLs:" -ForegroundColor Cyan
    Write-Host "   API: https://galera-volei.fly.dev/api/v1" -ForegroundColor White
    Write-Host "   Docs: https://galera-volei.fly.dev/docs" -ForegroundColor White
    
    Write-Host "`n📝 Comandos úteis:" -ForegroundColor Cyan
    Write-Host "   Ver logs: flyctl logs -a galera-volei" -ForegroundColor White
    Write-Host "   Abrir app: flyctl open -a galera-volei" -ForegroundColor White
    Write-Host "   Status: flyctl status -a galera-volei`n" -ForegroundColor White
    
    # Perguntar se quer abrir
    $open = Read-Host "Deseja abrir a aplicação no navegador? (S/N)"
    if ($open -eq "S" -or $open -eq "s") {
        flyctl open -a galera-volei
    }
} else {
    Write-Host "`n❌ ERRO NO DEPLOY!" -ForegroundColor Red
    Write-Host "   Verifique os logs: flyctl logs -a galera-volei`n" -ForegroundColor Yellow
    exit 1
}