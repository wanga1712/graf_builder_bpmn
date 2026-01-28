from __future__ import annotations

from pathlib import Path


class AppConfig:
    """
    Конфигурация приложения.
    """

    # Корневая директория проекта
    BASE_DIR: Path = Path(__file__).resolve().parent

    # Путь к файлу с сохранённым процессом
    PROCESS_FILE: Path = BASE_DIR / "process.json"


