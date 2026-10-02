import unittest
from decimal import Decimal

from materials import calculate_required_material

PRODUCT_COEFFICIENTS = {1: Decimal("2.5"), 2: Decimal("1"), 3: Decimal("1.1")}
MATERIAL_DEFECTS = {1: Decimal("0.5"), 2: Decimal("0"), 3: Decimal("1")}


def calc(product_type_id, material_type_id, quantity, param_1, param_2,
         coefficients=PRODUCT_COEFFICIENTS, defects=MATERIAL_DEFECTS):
    return calculate_required_material(
        product_type_id, material_type_id, quantity, param_1, param_2,
        coefficients, defects,
    )


class CalculateRequiredMaterialTest(unittest.TestCase):
    # Тест 1 (Стандартный): проверка обычного корректного расчета с известным результатом.
    def test_01_standard(self):
        # 3 * 4 * 2.5 = 30; * 10 = 300; * 1.005 = 301.5 -> 302
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0), 302)

    # Тест 2 (Округление): проверка, что дробный результат округляется строго
    # в большую сторону (вверх) до целого числа.
    def test_02_rounding(self):
        # 1 * 1 * 2.5 = 2.5 -> 3
        self.assertEqual(calc(1, 2, 1, 1.0, 1.0), 3)

    # Тест 3 (Несуществующий тип): проверка возврата -1 при передаче
    # некорректных ID типов продукции/материала.
    def test_03_unknown_type(self):
        self.assertEqual(calc(999, 1, 10, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 999, 10, 3.0, 4.0), -1)

    # Тест 4 (Отрицательные параметры): проверка возврата -1 при передаче
    # отрицательных размеров (param_1 или param_2).
    def test_04_negative_params(self):
        self.assertEqual(calc(1, 1, 10, -3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, -4.0), -1)
        self.assertEqual(calc(1, 1, 10, 0.0, 4.0), -1)

    # Тест 5 (Нулевое количество): проверка возврата -1, если количество
    # продукции равно нулю или меньше.
    def test_05_zero_quantity(self):
        self.assertEqual(calc(1, 1, 0, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, -5, 3.0, 4.0), -1)

    def test_exact_value_is_not_rounded_up(self):
        # 3 * 4 * 1 * 5 = 60, брак 0% -> ровно 60
        self.assertEqual(calc(2, 2, 5, 3.0, 4.0), 60)

    def test_float_error_does_not_add_extra_unit(self):
        # В float 1.1 * 10 = 11.000000000000002 -> ceil дал бы 12
        self.assertEqual(calc(2, 2, 1, 1.1, 10.0), 11)

    def test_integer_params_are_accepted(self):
        self.assertEqual(calc(2, 2, 2, 3, 4), 24)

    def test_float_and_int_reference_values_are_accepted(self):
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: 2.5}, {1: 0.5}), 302)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: 2}, {1: 0}), 240)

    def test_empty_reference_data(self):
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {}, {}), -1)

    def test_invalid_reference_data(self):
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, None, MATERIAL_DEFECTS), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, PRODUCT_COEFFICIENTS, None), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: None}, {1: 0.5}), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: "2.5"}, {1: 0.5}), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: 0}, {1: 0.5}), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: -2}, {1: 0.5}), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0, {1: 2.5}, {1: -1}), -1)

    def test_invalid_types(self):
        self.assertEqual(calc("1", 1, 10, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10.5, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10, "3", 4.0), -1)
        self.assertEqual(calc(True, 1, 10, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, None, 3.0, 4.0), -1)

    def test_nan_and_infinity(self):
        self.assertEqual(calc(1, 1, 10, float("nan"), 4.0), -1)
        self.assertEqual(calc(1, 1, 10, float("inf"), 4.0), -1)

    def test_function_is_deterministic_and_does_not_mutate_references(self):
        coefficients = {1: Decimal("2.5")}
        defects = {1: Decimal("0.5")}
        first = calc(1, 1, 10, 3.0, 4.0, coefficients, defects)
        second = calc(1, 1, 10, 3.0, 4.0, coefficients, defects)
        self.assertEqual(first, second)
        self.assertEqual(coefficients, {1: Decimal("2.5")})
        self.assertEqual(defects, {1: Decimal("0.5")})


if __name__ == "__main__":
    unittest.main()