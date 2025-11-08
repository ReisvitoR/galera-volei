# Script para deploy no Koyeb via GitHub
# O Koyeb fará deploy automático após o push

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "          PREPARAR DEPLOY NO KOYEB" -ForegroundColor White -BackgroundColor DarkCyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Verificar se está no diretório correto
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Erro: Dockerfile não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto.`n" -ForegroundColor Yellow
    exit 1
}

# Verificar Git
Write-Host "📋 Verificando Git..." -ForegroundColor Yellow
git status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git não configurado ou não inicializado!" -ForegroundColor Red
    Write-Host "Execute: git init && git remote add origin <URL>`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git OK`n" -ForegroundColor Green

# Verificar arquivos modificados
Write-Host "📋 Verificando alterações..." -ForegroundColor Yellow
$changes = git status --short
if ($changes) {
    Write-Host "Arquivos modificados:" -ForegroundColor Cyan
    Write-Host $changes -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✅ Nenhuma alteração para commitar`n" -ForegroundColor Green
    Write-Host "Quer fazer redeploy mesmo assim? (s/n): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -ne "s") {
        exit 0
    }
}

# Commit message
Write-Host "Digite a mensagem do commit (Enter para padrão): " -ForegroundColor Yellow -NoNewline
$commitMsg = Read-Host
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Deploy para Koyeb - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
}

# Git add
Write-Host "`n📦 Adicionando arquivos..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao adicionar arquivos!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Arquivos adicionados`n" -ForegroundColor Green

# Git commit
Write-Host "💾 Criando commit..." -ForegroundColor Yellow
git commit -m $commitMsg
$commitExitCode = $LASTEXITCODE
if ($commitExitCode -ne 0) {
    Write-Host "⚠️  Nada para commitar ou erro no commit" -ForegroundColor Yellow
    Write-Host "Continuando mesmo assim...`n" -ForegroundColor Gray
}

# Git push
Write-Host "🚀 Fazendo push para GitHub..." -ForegroundColor Yellow
git push origin main 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer push!" -ForegroundColor Red
    Write-Host "Verifique suas credenciais e conexão.`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Push realizado com sucesso!`n" -ForegroundColor Green

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "          DEPLOY INICIADO NO KOYEB!" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "O Koyeb detectará o push e iniciará o deploy automaticamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Acompanhe o deploy:" -ForegroundColor Yellow
Write-Host "   1. Acesse: https://app.koyeb.com/" -ForegroundColor White
Write-Host "   2. Vá para sua aplicação: galera-volei" -ForegroundColor White
Write-Host "   3. Acompanhe os logs em tempo real`n" -ForegroundColor White

Write-Host "⏱️  Tempo estimado: 3-5 minutos`n" -ForegroundColor Cyan

Write-Host "================================================================`n" -ForegroundColor Cyan

# Tentar abrir o dashboard
Write-Host "Deseja abrir o dashboard do Koyeb? (s/n): " -ForegroundColor Yellow -NoNewline
$openDashboard = Read-Host
if ($openDashboard -eq "s") {
    Start-Process "https://app.koyeb.com/"
}

Write-Host "`n🎉 Pronto! Aguarde o deploy finalizar no Koyeb.`n" -ForegroundColor Green
