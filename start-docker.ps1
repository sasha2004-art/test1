$ScriptPath = $PSScriptRoot

$ComposeFile = Join-Path -Path $ScriptPath -ChildPath "docker\docker-compose.yml"

Write-Host "Используется файл: $ComposeFile" -ForegroundColor Cyan
Write-Host "Запуск Docker контейнеров..." -ForegroundColor Green

docker-compose -f $ComposeFile up --build

Write-Host "Скрипт завершил работу." -ForegroundColor Yellow