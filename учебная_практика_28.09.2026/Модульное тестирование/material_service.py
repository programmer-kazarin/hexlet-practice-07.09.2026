import logging

from db import get_product_type_coefficient, get_material_defect_percent
from materials import calculate_required_material, ERROR_RESULT

logger = logging.getLogger(__name__)


def calculate_required_material_from_db(
    product_type_id: int,
    material_type_id: int,
    quantity: int,
    param_1: float,
    param_2: float,
) -> int:
    """Берет коэффициент и процент брака из БД и вызывает чистый расчет.
    При недоступности БД или любой другой ошибке возвращает -1."""
    try:
        coefficients = {product_type_id: get_product_type_coefficient(product_type_id)}
        defects = {material_type_id: get_material_defect_percent(material_type_id)}
    except Exception as lookup_error:
        logger.error("Не удалось получить данные справочников: %s", lookup_error)
        return ERROR_RESULT

    return calculate_required_material(
        product_type_id, material_type_id, quantity, param_1, param_2,
        coefficients, defects,
    )