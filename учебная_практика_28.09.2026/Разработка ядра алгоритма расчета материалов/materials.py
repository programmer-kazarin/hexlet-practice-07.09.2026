# materials.py (переписан, без зависимостей от БД)
"""Чистый расчет количества сырья: без БД, логирования и побочных эффектов."""
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation, ROUND_CEILING, localcontext

ERROR_RESULT = -1


def _is_int(value) -> bool:
    # bool является подклассом int, но True/False как ID или количество - ошибка
    return isinstance(value, int) and not isinstance(value, bool)


def _to_finite_decimal(value) -> Decimal | None:
    """int/float/Decimal -> Decimal (float через str, чтобы 1.1 не стало 1.1000000000000000888).
    Возвращает None, если значение не число или не конечное (NaN, inf)."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def calculate_required_material(
    product_type_id: int,
    material_type_id: int,
    quantity: int,
    param_1: float,
    param_2: float,
    product_type_coefficients: Mapping,
    material_defect_percents: Mapping,
) -> int:
    # --- Проверка входных данных ---
    if not _is_int(product_type_id) or not _is_int(material_type_id):
        return ERROR_RESULT
    if not _is_int(quantity) or quantity <= 0:
        return ERROR_RESULT

    first_param = _to_finite_decimal(param_1)
    second_param = _to_finite_decimal(param_2)
    if first_param is None or second_param is None:
        return ERROR_RESULT
    if first_param <= 0 or second_param <= 0:
        return ERROR_RESULT

    # --- Значения из справочников ---
    if not isinstance(product_type_coefficients, Mapping):
        return ERROR_RESULT
    if not isinstance(material_defect_percents, Mapping):
        return ERROR_RESULT

    coefficient = _to_finite_decimal(product_type_coefficients.get(product_type_id))
    defect_percent = _to_finite_decimal(material_defect_percents.get(material_type_id))
    if coefficient is None or defect_percent is None:
        return ERROR_RESULT  # ID не найден или значение не число
    if coefficient <= 0 or defect_percent < 0:
        return ERROR_RESULT  # некорректные данные справочника

    # --- Расчет в Decimal ---
    with localcontext() as context:
        context.prec = 50
        base_per_unit = first_param * second_param * coefficient
        clean_total = base_per_unit * quantity
        total_with_defect = clean_total * (1 + defect_percent / 100)
        return int(total_with_defect.to_integral_value(rounding=ROUND_CEILING))