set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )
COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"
VERIFY_SCRIPT="$PROJECT_ROOT/scripts/verify.sh"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${MAGENTA}===============================================${NC}"
echo -e "${MAGENTA} AI Quest Generator - Запуск и Верификация ${NC}"
echo -e "${MAGENTA}===============================================${NC}"

echo -e "\n${GREEN}[1/3] Запуск Docker контейнеров в фоновом режиме...${NC}"
docker compose -f "$COMPOSE_FILE" up --build -d

echo -e "\n${CYAN}[2/3] Ожидание инициализации сервисов (5 секунд)...${NC}"
sleep 5

echo -e "\n${YELLOW}[3/3] Запуск полного 7-этапного скрипта верификации...${NC}"
chmod +x "$VERIFY_SCRIPT"

if "$VERIFY_SCRIPT"; then
    echo -e "\n${GREEN}✅ ✅ ✅ ВЕРИФИКАЦИЯ УСПЕШНО ПРОЙДЕНА! ✅ ✅ ✅${NC}"
    echo -e "Контейнеры запущены в фоновом режиме."
    echo -e "Для просмотра логов используйте: ${CYAN}docker compose -f docker/docker-compose.yml logs -f${NC}"
    echo -e "Для остановки контейнеров используйте: ${CYAN}docker compose -f docker/docker-compose.yml down${NC}"
    exit 0
else
    echo -e "\n${RED}❌ ❌ ❌ ВЕРИФИКАЦИЯ ПРОВАЛЕНА! ❌ ❌ ❌${NC}"
    echo -e "${YELLOW}Останавливаем и удаляем контейнеры для чистоты окружения...${NC}"
    docker compose -f "$COMPOSE_FILE" down
    exit 1
fi