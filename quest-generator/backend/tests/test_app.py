import json
import unittest
from unittest.mock import patch
from backend.app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("backend.app.create_quest_from_setting")
    def test_generate_quest_endpoint_success(self, mock_create_quest):
        # Mock the return value of the quest generator
        mock_quest = {"questTitle": "Test Quest", "startNodeId": "1", "nodes": []}
        mock_create_quest.return_value = mock_quest

        # Send a POST request to the /generate endpoint
        response = self.app.post(
            "/generate",
            data=json.dumps({"setting": "A dark and stormy night", "api_key": "test_key"}),
            content_type="application/json",
        )

        # Check that the response is correct
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_quest)

    def test_generate_quest_endpoint_missing_data(self):
        # Send a POST request with missing data
        response = self.app.post(
            "/generate",
            data=json.dumps({"setting": "A dark and stormy night"}),
            content_type="application/json",
        )

        # Check that the response is a 400 error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Missing 'setting' or 'api_key' in request body"},
        )


if __name__ == "__main__":
    unittest.main()
