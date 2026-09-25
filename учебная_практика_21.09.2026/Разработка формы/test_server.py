import unittest
from unittest.mock import patch
from server import app


class TestApiPartners(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    @patch("server.get_partners_with_discount")
    def test_partners_endpoint_returns_data(self, mock_get_partners):
        mock_get_partners.return_value = [{
            "partner_id": 1,
            "company_name": 'ООО "Логистик-Экспресс"',
            "contact_email": "info@logex.ru",
            "phone": "+79991112233",
            "rating": 4.8,
            "total_quantity": 15000,
            "discount_percent": 5,
        }]
        response = self.client.get("/api/partners")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["discount_percent"], 5)

    @patch("server.get_partners_with_discount")
    def test_partners_endpoint_handles_empty_list(self, mock_get_partners):
        mock_get_partners.return_value = []
        response = self.client.get("/api/partners")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    @patch("server.get_partners_with_discount")
    def test_partners_endpoint_handles_null_fields_without_crash(self, mock_get_partners):
        mock_get_partners.return_value = [{
            "partner_id": 2,
            "company_name": "ИП Аномалия",
            "contact_email": None,
            "phone": None,
            "rating": None,
            "total_quantity": 0,
            "discount_percent": 0,
        }]
        response = self.client.get("/api/partners")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNone(data[0]["contact_email"])
        self.assertEqual(data[0]["discount_percent"], 0)

    @patch("server.get_partners_with_discount")
    def test_partners_endpoint_handles_db_failure_gracefully(self, mock_get_partners):
        mock_get_partners.side_effect = Exception("Соединение с БД потеряно")
        response = self.client.get("/api/partners")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), [])

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CRM", response.data)


if __name__ == "__main__":
    unittest.main()