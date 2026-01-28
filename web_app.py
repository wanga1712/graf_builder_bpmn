from __future__ import annotations

from typing import Any, Dict, List

from flask import Flask, jsonify, request, send_from_directory

from domain import ProcessGraph
from persistence import ProcessRepository


def create_app() -> Flask:
    """
    Создает и настраивает экземпляр Flask приложения.
    """
    app = Flask(__name__, static_folder=".", static_url_path="")
    repository = ProcessRepository()

    @app.route("/")
    def index() -> Any:
        """
        Возвращает основную HTML-страницу.
        """
        return send_from_directory(".", "web_index.html")

    @app.post("/api/process/from-text")
    def process_from_text() -> Any:
        """
        Создает простой линейный процесс из текстового списка шагов.

        Ожидает JSON вида:
        {
            "text": "Шаг 1\nШаг 2\nШаг 3"
        }
        """
        payload: Dict[str, Any] = request.get_json(force=True) or {}
        raw_text: str = payload.get("text", "")
        lines = raw_text.splitlines()

        graph = ProcessGraph.from_text_lines(lines)
        return jsonify(graph.to_dict())

    @app.post("/api/process/from-steps")
    def process_from_steps() -> Any:
        """
        Создает процесс из структурированного списка шагов.

        Ожидает JSON вида:
        {
            "steps": [
                {"title": "Шаг 1", "department": "Отдел_1"},
                {"title": "Шаг 2", "department": "Отдел_2"}
            ]
        }
        """
        payload: Dict[str, Any] = request.get_json(force=True) or {}
        steps: List[Dict[str, str]] = payload.get("steps") or []

        graph = ProcessGraph.from_structured_steps(steps)
        return jsonify(graph.to_dict())

    @app.post("/api/process/save")
    def save_process() -> Any:
        """
        Сохраняет текущий процесс (отделы и шаги) в JSON-файл.

        Ожидает JSON вида:
        {
            "departments": ["Отдел_1", "Отдел_2"],
            "steps": [
                {"title": "Шаг 1", "department": "Отдел_1"},
                {"title": "Шаг 2", "department": "Отдел_2"}
            ]
        }
        """
        payload: Dict[str, Any] = request.get_json(force=True) or {}
        departments: List[str] = payload.get("departments") or []
        steps: List[Dict[str, str]] = payload.get("steps") or []

        repository.save(departments=departments, steps=steps)
        return jsonify({"status": "ok"})

    @app.get("/api/process/load")
    def load_process() -> Any:
        """
        Загружает сохраненный процесс из JSON-файла, если он существует.
        """
        data = repository.load()
        return jsonify(data)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)

