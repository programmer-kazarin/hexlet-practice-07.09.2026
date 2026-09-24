import unittest
from discount import calculate_partner_discount


class TestCalculatePartnerDiscount(unittest.TestCase):

    def test_zero_quantity(self):
        self.assertEqual(calculate_partner_discount(0), 0)

    def test_below_first_threshold(self):
        self.assertEqual(calculate_partner_discount(9999), 0)

    def test_at_first_threshold(self):
        self.assertEqual(calculate_partner_discount(10000), 5)

    def test_below_second_threshold(self):
        self.assertEqual(calculate_partner_discount(49999), 5)

    def test_at_second_threshold(self):
        self.assertEqual(calculate_partner_discount(50000), 10)

    def test_below_third_threshold(self):
        self.assertEqual(calculate_partner_discount(299999), 10)

    def test_at_third_threshold(self):
        self.assertEqual(calculate_partner_discount(300000), 15)

    def test_large_quantity(self):
        self.assertEqual(calculate_partner_discount(1_000_000), 15)

    def test_none_value(self):
        self.assertEqual(calculate_partner_discount(None), 0)

    def test_negative_value(self):
        self.assertEqual(calculate_partner_discount(-100), 0)


if __name__ == "__main__":
    unittest.main()