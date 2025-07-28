import sys
from pathlib import Path
import webview
import shutil
from huggingface_hub import hf_hub_download
import json
import logging

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- РЕШЕНИЕ ПРОБЛЕМЫ ИМПОРТОВ ---
# Добавляем корневую папку проекта и папку app в пути поиска модулей
project_root = Path(__file__).parent
app_dir = project_root / "app"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))
# ------------------------------------

from app.main import app  # noqa: E402


class Api:
    """
    Этот класс предоставляет API, который будет доступен
    из JavaScript в окне PyWebView.
    """

    def __init__(self):
        self._window = None
        # --- ИСПРАВЛЕНИЕ: Добавляем собственный флаг для отслеживания состояния ---
        self._is_maximized = False

    def set_window(self, window):
        self._window = window

    def minimize(self):
        if self._window:
            self._window.minimize()

    def toggle_maximize(self):
        # --- ИСПРАВЛЕНИЕ: Используем наш собственный флаг, а не свойство окна ---
        if self._window:
            if self._is_maximized:
                self._window.restore()
            else:
                self._window.maximize()
            # Переключаем наш флаг после действия
            self._is_maximized = not self._is_maximized
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    def close(self):
        if self._window:
            self._window.destroy()

    def open_file_dialog(self):
        if not self._window:
            return
        file_types = ("GGUF-модели (*.gguf)",)
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=True, file_types=file_types
        )
        return result

    def save_quest_to_file(self, content: str):
        """
        Открывает диалог "Сохранить как..." для сохранения контента квеста.
        """
        if not self._window:
            return {"status": "error", "message": "Window not available"}

        # Попытаемся получить название квеста для имени файла по умолчанию
        default_filename = "quest.json"
        try:
            quest_data = json.loads(content)
            # Создаем безопасное имя файла из заголовка квеста
            if "questTitle" in quest_data and quest_data["questTitle"]:
                safe_title = "".join(
                    c
                    for c in quest_data["questTitle"]
                    if c.isalnum() or c in (" ", "_", "-")
                ).rstrip()
                default_filename = f"{safe_title}.json"
        except (json.JSONDecodeError, TypeError):
            # Игнорируем ошибки, если контент - невалидный JSON, используем имя по умолчанию
            pass

        file_types = ("JSON Files (*.json)", "All files (*.*)")
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename=default_filename, file_types=file_types
        )

        if result:
            try:
                # result - это уже строка (путь к файлу)
                with open(result, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "ok", "message": f"Файл сохранен в {result}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        return {"status": "cancelled", "message": "Сохранение отменено"}

    def manage_files(self, action: str, source_paths: list):
        if not source_paths:
            return {"status": "error", "message": "Файлы не были переданы."}

        target_dir = Path(__file__).parent / "quest-generator" / "models"
        target_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        error_count = 0
        messages = []

        for src_str in source_paths:
            source_path = Path(src_str)
            destination_path = target_dir / source_path.name
            try:
                if action == "copy":
                    shutil.copy2(source_path, destination_path)
                    messages.append(f"✅ Скопирован: {source_path.name}")
                elif action == "move":
                    shutil.move(str(source_path), str(destination_path))
                    messages.append(f"✅ Перемещен: {source_path.name}")
                success_count += 1
            except Exception as e:
                messages.append(f"❌ Ошибка с файлом {source_path.name}: {e}")
                error_count += 1

        final_message = "\n".join(messages)
        status = "ok" if error_count == 0 else "error"

        return {"status": status, "message": final_message}

    def download_model(self, repo_id, filename):
        """Скачивает модель из Hugging Face Hub в папку 'models'."""
        try:
            models_dir = Path.cwd() / "models"
            models_dir.mkdir(exist_ok=True)

            logger.info(f"Starting download: {repo_id}/{filename}")

            hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=models_dir,
                local_dir_use_symlinks=False,  # Рекомендуется для Windows
            )

            logger.info(f"Successfully downloaded {filename} to {models_dir}")
            return {
                "status": "ok",
                "message": f"Модель '{filename}' успешно скачана в папку 'models'.",
            }
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return {"status": "error", "message": f"Ошибка при скачивании: {e}"}


if __name__ == "__main__":
    api = Api()
    # --- ИЗМЕНЕНИЕ: Удалена передача иконки, вызывающая ошибку ---
    window = webview.create_window(
        "AI Quest Generator",
        app,
        js_api=api,
        width=1280,
        height=800,
        resizable=True,
        frameless=True,
        easy_drag=False,  # Управление перетаскиванием отдано CSS
    )
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---
    api.set_window(window)  # Передаем объект окна в API
    webview.start(debug=True)