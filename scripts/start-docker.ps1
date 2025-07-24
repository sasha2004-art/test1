# --- НАЧАЛО ФАЙЛА: scripts/start-docker.ps1 (ПРАВИЛЬНЫЙ КОД) ---
$ErrorActionPreference = "SilentlyContinue"

$ScriptPath = $PSScriptRoot
$ComposeFile = Join-Path -Path $ScriptPath -ChildPath "..\docker\docker-compose.yml"

Write-Host "===============================================" -ForegroundColor Magenta
Write-Host " AI Quest Generator - Запуск и Верификация " -ForegroundColor Magenta
Write-Host "==============================================="

Write-Host "`n[1/3] Запуск Docker контейнеров в фоновом режиме..." -ForegroundColor Green
docker-compose -f $ComposeFile up --build -d

Write-Host "`n[2/3] Ожидание инициализации сервисов (5 секунд)..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "`n[3/3] Запуск полного 7-этапного скрипта верификации..." -ForegroundColor Yellow

# Мы передаем bash простой, относительный путь в формате Unix,
# который он гарантированно поймет.
bash.exe -c "./scripts/verify.sh"

# Проверяем код выхода последней выполненной команды
if ($lastexitcode -eq 0) {
    # Если скрипт завершился успешно
    Write-Host "`n✅ ✅ ✅ ВЕРИФИКАЦИЯ УСПЕШНО ПРОЙДЕНА! ✅ ✅ ✅" -ForegroundColor Green
    Write-Host "Контейнеры запущены в фоновом режиме."
    Write-Host "Для просмотра логов используйте: " -NoNewline; Write-Host "docker-compose -f docker/docker-compose.yml logs -f" -ForegroundColor Cyan
    Write-Host "Для остановки контейнеров используйте: " -NoNewline; Write-Host "docker-compose -f docker/docker-compose.yml down" -ForegroundColor Cyan
    exit 0
} else {
    # Если скрипт завершился с ошибкой
    Write-Host "`n❌ ❌ ❌ ВЕРИФИКАЦИЯ ПРОВАЛЕНА! ❌ ❌ ❌" -ForegroundColor Red
    Write-Host "Останавливаем и удаляем контейнеры для чистоты окружения..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile down
    exit 1
}
# --- КОНЕЦ ФАЙЛА: scripts/start-docker.ps1 ---