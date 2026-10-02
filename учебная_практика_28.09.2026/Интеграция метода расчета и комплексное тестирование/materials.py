"""Расчет количества сырья для производства продукции."""
import logging
import math
from decimal import Decimal, InvalidOperation, ROUND_CEILING, localcontext

from db import get_product_type_coefficient, get_material_defect_percent

logger = logging.getLogger(__name__)

ERROR_RESULT = -1


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _to_positive_decimal(value) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    if not number.is_finite() or number <= 0:
        return None
    return number


def calculate_required_material(
    product_type_id: int,
    material_type_id: int,
    quantity: int,
    param_1: float,
    param_2: float,
    *,
    coefficient_provider=get_product_type_coefficient,
    defect_provider=get_material_defect_percent,
) -> int:
    """Рассчитывает необходимое количество материала с учетом брака.
    """
    try:
        if not _is_int(product_type_id) or not _is_int(material_type_id):
            return ERROR_RESULT
        if not _is_int(quantity) or quantity <= 0:
            return ERROR_RESULT

        first_param = _to_positive_decimal(param_1)
        second_param = _to_positive_decimal(param_2)
        if first_param is None or second_param is None:
            return ERROR_RESULT

        coefficient_raw = coefficient_provider(product_type_id)
        defect_raw = defect_provider(material_type_id)
        if coefficient_raw is None or defect_raw is None:
            return ERROR_RESULT  # несуществующий тип продукции или материала

        coefficient = Decimal(str(coefficient_raw))
        defect_percent = Decimal(str(defect_raw))
        if coefficient <= 0 or defect_percent < 0:
            return ERROR_RESULT  # некорректные данные в справочнике

        with localcontext() as context:
            context.prec = 50
            base_per_unit = first_param * second_param * coefficient
            clean_total = base_per_unit * quantity
            total_with_defect = clean_total * (1 + defect_percent / 100)
            return int(total_with_defect.to_integral_value(rounding=ROUND_CEILING))

    except Exception as calculation_error:
        logger.error("Ошибка расчета материала: %s", calculation_error)
        return ERROR_RESULT