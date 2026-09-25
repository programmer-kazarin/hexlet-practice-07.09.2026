from decimal import Decimal
from flask import Flask, jsonify, render_template, request, redirect, url_for
from db import (
    get_partners_with_discount,
    get_partner_by_id,
    create_partner,
    update_partner,
    PartnerNotFoundError,
    DuplicateInnError,
)

app = Flask(__name__, static_folder="static", template_folder="templates")

REQUIRED_FIELDS = [
    "company_name", "partner_type", "inn",
    "address", "director_name", "contact_email", "phone", "rating",
]


def serialize_partner(partner: dict) -> dict:
    serialized = {}
    for key, value in partner.items():
        if isinstance(value, Decimal):
            serialized[key] = float(value)
        else:
            serialized[key] = value
    return serialized


def validate_partner_payload(payload: dict) -> str | None:
    for field in REQUIRED_FIELDS:
        if not payload.get(field):
            return f"Поле '{field}' обязательно для заполнения"
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/partners")
def api_partners():
    try:
        partners = get_partners_with_discount()
        serialized_partners = [serialize_partner(p) for p in partners]
        return jsonify(serialized_partners), 200
    except Exception as server_error:
        app.logger.error(f"Ошибка при получении партнеров: {server_error}")
        return jsonify([]), 500


@app.route("/api/partners/<int:partner_id>")
def api_partner_detail(partner_id):
    try:
        partner = get_partner_by_id(partner_id)
        return jsonify(serialize_partner(partner)), 200
    except PartnerNotFoundError:
        return jsonify({"error": "Партнер не найден"}), 404


@app.route("/api/partners", methods=["POST"])
def api_create_partner():
    payload = request.get_json(silent=True) or {}

    validation_error = validate_partner_payload(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        new_id = create_partner(payload)
        return jsonify({"partner_id": new_id}), 201
    except DuplicateInnError as duplicate_error:
        return jsonify({"error": str(duplicate_error)}), 409
    except Exception as server_error:
        app.logger.error(f"Ошибка создания партнера: {server_error}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/api/partners/<int:partner_id>", methods=["PUT"])
def api_update_partner(partner_id):
    payload = request.get_json(silent=True) or {}

    validation_error = validate_partner_payload(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        update_partner(partner_id, payload)
        return jsonify({"partner_id": partner_id}), 200
    except PartnerNotFoundError as not_found_error:
        return jsonify({"error": str(not_found_error)}), 404
    except DuplicateInnError as duplicate_error:
        return jsonify({"error": str(duplicate_error)}), 409
    except Exception as server_error:
        app.logger.error(f"Ошибка обновления партнера: {server_error}")
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

    return render_template("partner_edit.html", mode="edit", partner=partner)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)