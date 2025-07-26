import argparse
import os
import shutil
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from dotenv import load_dotenv
except ImportError:
    print("Ошибка: пакет python-dotenv не найден. Установите его: pip install python-dotenv")
    sys.exit(1)


def main():
    """Скрипт для копирования или перемещения файлов моделей в целевую директорию."""
    parser = argparse.ArgumentParser(
        description="Управление файлами локальных моделей GGUF."
    )
    parser.add_argument(
        "source_files",
        type=str,
        nargs='+',  # <--- Ключевое изменение: принимаем один или несколько файлов
        help="Полные пути к исходным .gguf файлам моделей (через пробел)."
    )
    parser.add_argument(
        "--action",
        type=str,
        choices=["copy", "move"],
        default="copy",
        help="Действие: 'copy' для копирования, 'move' для перемещения (вырезания)."
    )
    args = parser.parse_args()

    # --- Загрузка пути назначения из .env файла ---
    env_path = project_root / "quest-generator" / ".env"
    if not env_path.exists():
        print(f"Ошибка: Файл окружения не найден по пути {env_path}")
        print("Пожалуйста, запустите 'python start.py' один раз, чтобы сгенерировать его.")
        sys.exit(1)

    load_dotenv(dotenv_path=env_path)
    target_dir_str = os.getenv("LOCAL_MODEL_TARGET_PATH")

    if not target_dir_str:
        print("Ошибка: Переменная LOCAL_MODEL_TARGET_PATH не найдена в .env файле.")
        sys.exit(1)

    target_dir = Path(target_dir_str)
    target_dir.mkdir(parents=True, exist_ok=True)

    # --- Обработка каждого файла ---
    for source_file_str in args.source_files:
        source_path = Path(source_file_str)
        print(f"\n--- Обработка файла: {source_path.name} ---")

        if not source_path.exists() or not source_path.is_file():
            print(f"❌ Ошибка: Исходный файл не найден или не является файлом: {source_path}")
            continue # Пропускаем этот файл и переходим к следующему

        if not source_path.name.endswith(".gguf"):
            print(f"⚠️  Предупреждение: Файл '{source_path.name}' не имеет расширения .gguf.")

        destination_path = target_dir / source_path.name

        if destination_path.exists():
            overwrite = input(f"Файл '{destination_path.name}' уже существует. Перезаписать? (y/n): ").lower()
            if overwrite != 'y':
                print("Операция отменена для этого файла.")
                continue

        try:
            if args.action == "copy":
                print(f"Копирование файла из '{source_path}' в '{destination_path}'...")
                shutil.copy2(source_path, destination_path)
                print("✅ Копирование успешно завершено!")
            elif args.action == "move":
                print(f"Перемещение файла из '{source_path}' в '{destination_path}'...")
                shutil.move(str(source_path), str(destination_path))
                print("✅ Перемещение успешно завершено!")
        except Exception as e:
            print(f"❌ Произошла ошибка при обработке файла: {e}")

if __name__ == "__main__":
    main()