import os
import sys
import subprocess
from pathlib import Path


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def setup_environment():
    """Находит и записывает абсолютный путь к папке с моделями в .env файл."""
    try:
        project_root = Path(__file__).parent.resolve()
        models_dir = project_root / "quest-generator" / "models"
        env_file_path = project_root / "quest-generator" / ".env"

        models_dir.mkdir(parents=True, exist_ok=True)

        env_content = f"LOCAL_MODEL_TARGET_PATH={models_dir.as_posix()}"

        env_file_path.write_text(env_content)
        print(f"{Colors.OKGREEN}Переменная окружения для моделей настроена в: {env_file_path}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Не удалось настроить .env файл для моделей: {e}{Colors.ENDC}")
        return False


def check_docker_installed():
    """Проверяет, установлен ли Docker и доступен ли он в PATH."""
    print(f"{Colors.OKBLUE}Проверка наличия Docker...{Colors.ENDC}")
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"{Colors.OKGREEN}Docker найден! Продолжаем...{Colors.ENDC}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            f"\n{Colors.FAIL}ОШИБКА: Docker не найден или сервис Docker не запущен.{Colors.ENDC}"
        )
        print(
            f"{Colors.WARNING}Этот проект требует Docker для работы. Пожалуйста, установите Docker Desktop и убедитесь, что он запущен.{Colors.ENDC}"
        )
        print(
            f"Ссылка для скачивания: {Colors.UNDERLINE}https://www.docker.com/products/docker-desktop/{Colors.ENDC}\n"
        )
        return False


def run_command(command):
    """Запускает команду и передает ее вывод в консоль."""
    try:
        process = subprocess.run(command, shell=True, check=True)
        return process.returncode
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}Ошибка выполнения скрипта: {e}{Colors.ENDC}")
        return e.returncode
    except FileNotFoundError:
        print(
            f"{Colors.FAIL}Команда не найдена. Убедитесь, что у вас установлены необходимые инструменты.{Colors.ENDC}"
        )
        return 1


def main():
    """Главная функция для определения ОС и запуска соответствующего скрипта."""
    print(f"{Colors.HEADER}====================================={Colors.ENDC}")
    print(f"{Colors.HEADER}  Универсальный Запускатор Проекта  {Colors.ENDC}")
    print(f"{Colors.HEADER}====================================={Colors.ENDC}\n")

    if not setup_environment():
        sys.exit(1)

    if not check_docker_installed():
        sys.exit(1)

    script_dir = "scripts"
    linux_script = os.path.join(script_dir, "start-docker.sh")
    windows_script = os.path.join(script_dir, "start-docker.ps1")

    if os.name == "posix":
        print(
            f"\n{Colors.OKCYAN}Обнаружена Linux/macOS. Запуск {linux_script}...{Colors.ENDC}\n"
        )
        run_command(f"chmod +x {linux_script}")
        return_code = run_command(f"./{linux_script}")
    elif os.name == "nt":
        print(
            f"\n{Colors.OKCYAN}Обнаружена Windows. Запуск {windows_script}...{Colors.ENDC}\n"
        )
        command = f"powershell.exe -ExecutionPolicy Bypass -File .\\{windows_script}"
        return_code = run_command(command)
    else:
        print(
            f"\n{Colors.FAIL}Неподдерживаемая операционная система: {os.name}{Colors.ENDC}"
        )
        return_code = 1

    sys.exit(return_code)


if __name__ == "__main__":
    main()