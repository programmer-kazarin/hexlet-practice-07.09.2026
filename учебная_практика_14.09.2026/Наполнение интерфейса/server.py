from decimal import Decimal
from flask import Flask, jsonify, render_template
from db import get_partners_with_discount

app = Flask(__name__, static_folder="static", template_folder="templates")


def serialize_partner(partner: dict) -> dict:
    """Приводит значения Decimal к float/None для корректной JSON-сериализации."""
    serialized = {}
    for key, value in partner.items():
        if isinstance(value, Decimal):
            serialized[key] = float(value)
        else:
            serialized[key] = value
    return serialized


@app.route("/")
def index():
    """Отдает главную HTML-страницу приложения."""
    return render_template("index.html")


@app.route("/api/partners")
def api_partners():
    """
    Отдает список партнеров с их скидками в формате JSON.
    Не падает при отсутствии данных или ошибке подключения к БД —
    в таких случаях возвращает пустой список с корректным статусом.
    """
    try:
        partners = get_partners_with_discount()
        serialized_partners = [serialize_partner(partner) for partner in partners]
        return jsonify(serialized_partners), 200
    except Exception as server_error:
        app.logger.error(f"Ошибка при получении партнеров: {server_error}")
        return jsonify([]), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)