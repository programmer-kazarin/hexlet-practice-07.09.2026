import unittest
from decimal import Decimal

from materials import calculate_required_material

# Мок-справочники
PRODUCT_COEFFICIENTS = {1: Decimal("2.5"), 2: Decimal("1"), 3: Decimal("1.1")}
MATERIAL_DEFECTS = {1: Decimal("0.5"), 2: Decimal("0"), 3: Decimal("1")}


def fake_coefficient(product_type_id):
    return PRODUCT_COEFFICIENTS.get(product_type_id)


def fake_defect(material_type_id):
    return MATERIAL_DEFECTS.get(material_type_id)


def calc(product_type_id, material_type_id, quantity, param_1, param_2):
    return calculate_required_material(
        product_type_id, material_type_id, quantity, param_1, param_2,
        coefficient_provider=fake_coefficient,
        defect_provider=fake_defect,
    )


class CalculateRequiredMaterialTest(unittest.TestCase):
    def test_basic_calculation_with_defect(self):
        # 3 * 4 * 2.5 = 30; * 10 = 300; * 1.005 = 301.5 -> 302
        self.assertEqual(calc(1, 1, 10, 3.0, 4.0), 302)

    def test_exact_value_is_not_rounded_up(self):
        # 3 * 4 * 1 * 5 = 60, брак 0% -> ровно 60
        self.assertEqual(calc(2, 2, 5, 3.0, 4.0), 60)

    def test_float_error_does_not_add_extra_unit(self):
        # В float 1.1 * 10 = 11.000000000000002 -> ceil дал бы 12
        self.assertEqual(calc(2, 2, 1, 1.1, 10.0), 11)

    def test_integer_params_are_accepted(self):
        self.assertEqual(calc(2, 2, 2, 3, 4), 24)

    def test_unknown_product_type(self):
        self.assertEqual(calc(999, 1, 10, 3.0, 4.0), -1)

    def test_unknown_material_type(self):
        self.assertEqual(calc(1, 999, 10, 3.0, 4.0), -1)

    def test_non_positive_quantity(self):
        self.assertEqual(calc(1, 1, 0, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, -5, 3.0, 4.0), -1)

    def test_negative_or_zero_params(self):
        self.assertEqual(calc(1, 1, 10, -3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10, 3.0, -4.0), -1)
        self.assertEqual(calc(1, 1, 10, 0.0, 4.0), -1)

    def test_invalid_types(self):
        self.assertEqual(calc("1", 1, 10, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10.5, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, 10, "3", 4.0), -1)
        self.assertEqual(calc(True, 1, 10, 3.0, 4.0), -1)
        self.assertEqual(calc(1, 1, None, 3.0, 4.0), -1)

    def test_nan_and_infinity(self):
        self.assertEqual(calc(1, 1, 10, float("nan"), 4.0), -1)
        self.assertEqual(calc(1, 1, 10, float("inf"), 4.0), -1)

if __name__ == "__main__":
    unittest.main()