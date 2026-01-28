from __future__ import annotations

import json
from typing import Any, Dict, List

from config import AppConfig


class ProcessRepository:
    """
    Хранилище процесса, основанное на JSON-файле.
    """

    def __init__(self) -> None:
        """
        Инициализирует репозиторий с использованием пути из конфигурации.
        """
        self._path = AppConfig.PROCESS_FILE

    def save(self, departments: List[str], steps: List[Dict[str, Any]]) -> None:
        """
        Сохраняет отделы и шаги процесса в файл.
        """
        data = {
            "departments": departments,
            "steps": steps,
        }
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> Dict[str, Any]:
        """
        Загружает отделы и шаги процесса из файла, если он существует.
        """
        if not self._path.exists():
            return {"departments": [], "steps": []}

        raw = self._path.read_text(encoding="utf-8")
        data: Dict[str, Any] = json.loads(raw)
        return {
            "departments": data.get("departments") or [],
            "steps": data.get("steps") or [],
        }


