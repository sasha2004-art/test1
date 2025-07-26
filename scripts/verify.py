import subprocess
import sys
from pathlib import Path

class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def run_check(name, command, cwd, python_executable):
    """
    Запускает проверку и выводит результат.
    Использует захват вывода для чистоты логов.
    """
    print(f"\n{Colors.HEADER}--- {name} ---{Colors.ENDC}")
    
    full_command = [str(python_executable), "-m"] + command
    
    try:
        process = subprocess.run(
            full_command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        print(f"{Colors.OKGREEN}✅ Проверка пройдена успешно.{Colors.ENDC}")
        if process.stdout.strip():
            print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Проверка провалена!{Colors.ENDC}")
        if e.stdout.strip():
            print("--- STDOUT ---")
            print(e.stdout)
        if e.stderr.strip():
            print("--- STDERR ---")
            print(e.stderr)
        return False

def main():
    """Главный скрипт верификации проекта."""
    project_root = Path(__file__).parent.parent
    venv_dir = project_root / ".venv"
    
    if not venv_dir.exists():
        print(f"{Colors.FAIL}Виртуальное окружение не найдено. Пожалуйста, запустите 'python start.py' сначала.{Colors.ENDC}")
        sys.exit(1)
        
    python_executable = venv_dir / "Scripts" / "python.exe" if sys.platform == "win32" else venv_dir / "bin" / "python"

    checks = [
        ("1. Formatting (black)", ["black", "--check", "."]),
        ("2. Linting (flake8)", ["flake8", ".", "--count", "--ignore=E501,W503", "--show-source", "--statistics"]),
        ("3. Type Checking (pyright)", ["pyright"]),
        ("4. Dependency Security (pip-audit)", ["pip_audit"]),
        ("5. Code Security (bandit)", ["bandit", "-r", ".", "-x", "./tests"]),
        ("6. Static Analysis (semgrep)", ["semgrep", "scan", "--config", "p/python", "--metrics=off"]),
        ("7. Unit Tests (pytest)", ["pytest", "--cov=app", "--cov-report=term-missing", "--cov-fail-under=90"]),
    ]

    print(f"{Colors.BOLD}🚀 Запуск полной 7-этапной верификации проекта...{Colors.ENDC}")
    
    all_passed = True
    for name, command in checks:
        if not run_check(name, command, project_root, python_executable):
            all_passed = False

    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ✅ ✅ ВЕРИФИКАЦИЯ УСПЕШНО ПРОЙДЕНА! ✅ ✅ ✅{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ ❌ ❌ ВЕРИФИКАЦИЯ ПРОВАЛЕНА! ❌ ❌ ❌{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()