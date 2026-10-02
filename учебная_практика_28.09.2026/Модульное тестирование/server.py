import logging
import re
from decimal import Decimal
from pathlib import Path

from flask import Flask, jsonify, render_template, request, redirect, url_for
from db import (
    get_partners_with_discount,
    get_partner_by_id,
    get_partner_sales_history,
    create_partner,
    update_partner,
    PartnerNotFoundError,
    DuplicateInnError,
    DuplicateEmailError,
    DatabaseUnavailableError,
)
from material_service import calculate_required_material_from_db

app = Flask(__name__, static_folder="static", template_folder="templates")
logger = logging.getLogger(__name__)
LOG_PATH = Path(__file__).resolve().parent / "app.log"


def configure_error_log():
    """Пишет ошибки в app.log и в консоль: дата, время и текст."""
    root = logging.getLogger()
    log_path = LOG_PATH.resolve()
    if any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == log_path
        for handler in root.handlers
    ):
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    root.setLevel(logging.ERROR)
    root.addHandler(file_handler)
    root.addHandler(console_handler)


configure_error_log()

# rating проверяется отдельно: он необязателен и по умолчанию равен 0
REQUIRED_FIELDS = [
    "company_name", "partner_type", "inn",
    "address", "director_name", "contact_email", "phone",
]

CALCULATION_FIELDS = [
    "product_type_id", "material_type_id", "quantity", "param_1", "param_2",
]
CALCULATION_FAILURE_MESSAGE = (
    "Расчет невозможен: проверьте, что типы продукции и материала существуют, "
    "а количество и параметры положительные"
)
INN_PATTERN = re.compile(r"^\d{10}(\d{2})?$")
PHONE_PATTERN = re.compile(r"^\+7\s?\(?\d{3}\)?\s?\d{3}-?\d{2}-?\d{2}$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def serialize_partner(partner: dict) -> dict:
    serialized = {}
    for key, value in partner.items():
        serialized[key] = float(value) if isinstance(value, Decimal) else value
    return serialized


def validate_partner_payload(payload: dict) -> str | None:
    """Server-side дублирование клиентской валидации - форма может быть
    вызвана напрямую через API в обход браузера, поэтому проверка нужна и здесь."""
    if not payload.get("company_name"):
        return "Наименование не должно быть пустым"
    if not payload.get("contact_email"):
        return "Email не должен быть пустым"

    rating = payload.get("rating")
    if rating is not None:
        try:
            rating_int = int(rating)
            if rating_int < 0 or rating_int != float(rating):
                return "Рейтинг должен быть целым неотрицательным числом"
        except (ValueError, TypeError):
            return "Рейтинг должен быть целым неотрицательным числом"

    for field in REQUIRED_FIELDS:
        if not payload.get(field):
            return f"Поле '{field}' обязательно для заполнения"

    if not INN_PATTERN.fullmatch(str(payload["inn"]).strip()):
        return "ИНН должен содержать 10 цифр (юрлицо) или 12 цифр (ИП)"
    if not PHONE_PATTERN.fullmatch(str(payload["phone"]).strip()):
        return "Телефон должен быть в формате +7 (999) 123-45-67"
    if not EMAIL_PATTERN.fullmatch(str(payload["contact_email"]).strip()):
        return "Введите действующий email, например info@company.ru"
    return None


def normalize_payload(payload: dict) -> dict:
    """Вызывается после успешной валидации: приводит rating к int (по умолчанию 0)."""
    normalized = dict(payload)
    normalized["rating"] = int(payload.get("rating") or 0)
    return normalized

def validate_calculation_payload(payload) -> str | None:
    """Проверяет только форму запроса. Допустимость значений решает сам метод расчета:
    отрицательные числа и несуществующие ID дойдут до него и вернутся как -1."""
    if not isinstance(payload, dict):
        return "Ожидается JSON-объект с параметрами расчета"
    for field in CALCULATION_FIELDS:
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"Поле '{field}' должно быть числом"
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/partners")
def api_partners():
    try:
        partners = get_partners_with_discount()
        return jsonify([serialize_partner(p) for p in partners]), 200
    except DatabaseUnavailableError as db_error:
        # Фронтенд получает 503 и показывает понятную ошибку вместо белого экрана
        logger.error("База данных недоступна при получении партнеров: %s", db_error)
        return jsonify({"error": "База данных временно недоступна"}), 503
    except Exception as server_error:
        logger.error("Ошибка при получении партнеров: %s", server_error)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/api/partners/<int:partner_id>")
def api_partner_detail(partner_id):
    try:
        return jsonify(serialize_partner(get_partner_by_id(partner_id))), 200
    except PartnerNotFoundError:
        return jsonify({"error": "Партнер не найден"}), 404
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при получении партнера: %s", db_error)
        return jsonify({"error": "База данных временно недоступна"}), 503


@app.route("/api/partners/<int:partner_id>/history")
def api_partner_history(partner_id):
    try:
        return jsonify(get_partner_sales_history(partner_id)), 200
    except PartnerNotFoundError:
        return jsonify({"error": "Партнер не найден"}), 404
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при получении истории продаж: %s", db_error)
        return jsonify({"error": "База данных временно недоступна"}), 503
    except Exception as server_error:
        logger.error("Ошибка получения истории продаж: %s", server_error)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/api/partners", methods=["POST"])
def api_create_partner():
    payload = request.get_json(silent=True) or {}

    validation_error = validate_partner_payload(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        new_id = create_partner(normalize_payload(payload))
        return jsonify({"partner_id": new_id}), 201
    except (DuplicateInnError, DuplicateEmailError) as duplicate_error:
        return jsonify({"error": str(duplicate_error)}), 409
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при создании партнера: %s", db_error)
        return jsonify({"error": str(db_error)}), 503
    except Exception as server_error:
        logger.error("Ошибка создания партнера: %s", server_error)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/api/partners/<int:partner_id>", methods=["PUT"])
def api_update_partner(partner_id):
    payload = request.get_json(silent=True) or {}

    validation_error = validate_partner_payload(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        update_partner(partner_id, normalize_payload(payload))
        return jsonify({"partner_id": partner_id}), 200
    except PartnerNotFoundError as not_found_error:
        return jsonify({"error": str(not_found_error)}), 404
    except (DuplicateInnError, DuplicateEmailError) as duplicate_error:
        return jsonify({"error": str(duplicate_error)}), 409
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при обновлении партнера: %s", db_error)
        return jsonify({"error": str(db_error)}), 503
    except Exception as server_error:
        logger.error("Ошибка обновления партнера: %s", server_error)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/partners/new")
def partner_new():
    return render_template("partner_edit.html", mode="add", partner=None)


@app.route("/partners/<int:partner_id>/edit")
def partner_edit(partner_id):
    try:
        partner = get_partner_by_id(partner_id)
    except PartnerNotFoundError:
        return redirect(url_for("index"))
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при открытии карточки партнера: %s", db_error)
        return redirect(url_for("index"))

    return render_template("partner_edit.html", mode="edit", partner=partner)


@app.route("/partners/<int:partner_id>/history")
def partner_history(partner_id):
    try:
        partner = get_partner_by_id(partner_id)
    except PartnerNotFoundError:
        return redirect(url_for("index"))
    except DatabaseUnavailableError as db_error:
        logger.error("База данных недоступна при открытии истории партнера: %s", db_error)
        return redirect(url_for("index"))

    return render_template("partner_history.html", partner=partner)


@app.route("/calculator")
def calculator_page():
    return render_template("material_calculator.html")


@app.route("/api/calculate-material", methods=["POST"])
def api_calculate_material():
    payload = request.get_json(silent=True)

    validation_error = validate_calculation_payload(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    result = calculate_required_material_from_db(
        payload["product_type_id"],
        payload["material_type_id"],
        payload["quantity"],
        payload["param_1"],
        payload["param_2"],
    )
    if result == -1:
        return jsonify({"error": CALCULATION_FAILURE_MESSAGE}), 422
    return jsonify({"result": result}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)