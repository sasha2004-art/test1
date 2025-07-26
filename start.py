import sys
import subprocess
import venv
from pathlib import Path
import os

class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

def run_command_live(command):
    try:
        subprocess.run(command, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"{Colors.FAIL}Ошибка выполнения команды '{' '.join(map(str, command))}': {e}{Colors.ENDC}")
        return False

def setup_environment(project_root, use_local_llm):
    """Создает .env файл с настройками."""
    env_file_path = project_root / ".env"
    with open(env_file_path, "w") as f:
        f.write(f"USE_LOCAL_LLM={str(use_local_llm).lower()}\n")
    print(f"{Colors.OKGREEN}.env файл сконфигурирован.{Colors.ENDC}")

def main():
    print(f"{Colors.HEADER}--- AI Quest Generator: Desktop Setup ---{Colors.ENDC}")
    project_root = Path(__file__).parent
    venv_dir = project_root / ".venv"

    # --- Интерактивный выбор ---
    choice = input(f"{Colors.WARNING}Хотите установить поддержку локальных LLM (llama.cpp)? (y/n): {Colors.ENDC}").lower().strip()
    use_local_llm = (choice == 'y')
    
    setup_environment(project_root, use_local_llm)

    if not venv_dir.exists():
        print(f"{Colors.OKBLUE}Создание виртуального окружения...{Colors.ENDC}")
        venv.create(venv_dir, with_pip=True)
        print(f"{Colors.OKGREEN}Виртуальное окружение создано.{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}Виртуальное окружение найдено.{Colors.ENDC}")

    python_executable = venv_dir / "Scripts" / "python.exe" if sys.platform == "win32" else venv_dir / "bin" / "python"

    print(f"\n{Colors.OKBLUE}Установка зависимостей...{Colors.ENDC}")
    if not run_command_live([python_executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        sys.exit(1)
    print(f"{Colors.OKGREEN}Основные зависимости установлены.{Colors.ENDC}")
    
    # --- Установка llama-cpp-python по условию ---
    if use_local_llm:
        print(f"\n{Colors.OKBLUE}Установка llama-cpp-python с поддержкой GPU (NVIDIA)...{Colors.ENDC}")
        env = {**os.environ, 'CMAKE_ARGS': '-DLLAMA_CUBLAS=on', 'FORCE_CMAKE': '1'}
        llama_install_command = [
            python_executable, "-m", "pip", "install", "llama-cpp-python",
            "--force-reinstall", "--no-cache-dir", "--no-binary", ":all:"
        ]
        try:
            subprocess.run(llama_install_command, env=env, check=True)
            print(f"{Colors.OKGREEN}llama-cpp-python успешно установлен!{Colors.ENDC}")
        except subprocess.CalledProcessError:
            print(f"{Colors.FAIL}Не удалось установить llama-cpp-python.{Colors.ENDC}")
            print(f"{Colors.WARNING}Убедитесь, что установлены 'Visual Studio Build Tools' и NVIDIA CUDA Toolkit.{Colors.ENDC}")
            sys.exit(1)
    else:
        print(f"\n{Colors.OKBLUE}Пропускаем установку llama-cpp-python.{Colors.ENDC}")

    print(f"\n{Colors.OKGREEN}Установка завершена. Запуск приложения...{Colors.ENDC}")
    if not run_command_live([python_executable, "run_desktop.py"]):
        sys.exit(1)

if __name__ == "__main__":
    main()