import json
import unittest
from unittest.mock import patch

from gistapi.gistapi import app


class GistApiTestCase(unittest.TestCase):
    """Test case for the Gist API."""

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def mock_gists_response(self, url, params=None, **kwargs):
        """Mock the response from the GitHub API for gists."""
        if "gists" in url:
            mock_response = unittest.mock.Mock()
            mock_response.status_code = 200
            page = params.get("page", 1)
            if page == 1:
                mock_response.json.return_value = [
                    {
                        "id": "1",
                        "files": {
                            "file1.py": {
                                "raw_url": "https://gist.githubusercontent.com/raw/1"
                            }
                        },
                        "html_url": "https://gist.github.com/1",
                    }
                ]
            elif page == 2:
                mock_response.json.return_value = [
                    {
                        "id": "2",
                        "files": {
                            "file2.py": {
                                "raw_url": "https://gist.githubusercontent.com/raw/2"
                            }
                        },
                        "html_url": "https://gist.github.com/2",
                    }
                ]
            else:
                mock_response.json.return_value = []
            return mock_response
        else:
            mock_response = unittest.mock.Mock()
            mock_response.status_code = 200
            if url == "https://gist.githubusercontent.com/raw/1":
                mock_response.text = "import requests"
            elif url == "https://gist.githubusercontent.com/raw/2":
                mock_response.text = "some other content"
            return mock_response

    def test_ping(self):
        """Test the /ping endpoint."""
        response = self.app.get("/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"pong")

    @patch("gistapi.gistapi.requests.get")
    def test_search_valid(self, mock_get):
        """Test the search endpoint with valid parameters."""
        mock_get.side_effect = self.mock_gists_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": "justdionysus", "pattern": "import requests"}),
            content_type="application/json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)
        self.assertEqual(len(data["matches"]), 1)

    @patch("gistapi.gistapi.requests.get")
    def test_search_invalid_username(self, mock_get):
        """Test the search endpoint with an invalid username."""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps(
                {"username": "invalidusername", "pattern": "import requests"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Error fetching gists from GitHub", response.data)

    def test_search_invalid_pattern(self):
        """Test the search endpoint with an invalid regex pattern."""
        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": "justdionysus", "pattern": "[invalid"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid regex pattern", response.data)

    def test_search_missing_parameters(self):
        """Test the search endpoint with missing parameters."""
        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": "justdionysus"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"username and pattern are required", response.data)

    def test_search_empty_username_and_pattern(self):
        """Test the search endpoint with empty username and pattern."""
        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": "", "pattern": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"username and pattern are required", response.data)

    @patch("gistapi.gistapi.requests.get")
    def test_search_special_characters_username_and_pattern(self, mock_get):
        """Test the search endpoint with special characters in username and pattern."""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": "@#$%^&", "pattern": "!@#$%^&*()"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Error fetching gists from GitHub", response.data)

    @patch("gistapi.gistapi.requests.get")
    def test_search_long_username_and_pattern(self, mock_get):
        """Test the search endpoint with a very long username and pattern."""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        long_username = "a" * 500
        long_pattern = "b" * 500
        response = self.app.post(
            "/api/v1/search",
            data=json.dumps({"username": long_username, "pattern": long_pattern}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Error fetching gists from GitHub", response.data)

    @patch("gistapi.gistapi.requests.get")
    def test_search_complex_pattern(self, mock_get):
        """Test the search endpoint with a complex regex pattern."""
        mock_get.side_effect = self.mock_gists_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps(
                {
                    "username": "justdionysus",
                    "pattern": "^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[a-zA-Z0-9-.]+$",
                }
            ),
            content_type="application/json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)

    @patch("gistapi.gistapi.requests.get")
    def test_search_no_matching_gists(self, mock_get):
        """Test the search endpoint with no matching gists."""
        mock_get.side_effect = self.mock_gists_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps(
                {"username": "justdionysus", "pattern": "nonexistentpattern"}
            ),
            content_type="application/json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["matches"]), 0)

    @patch("gistapi.gistapi.requests.get")
    def test_search_with_pagination_first_page(self, mock_get):
        """Test the search endpoint with pagination, first page."""
        mock_get.side_effect = self.mock_gists_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps(
                {
                    "username": "justdionysus",
                    "pattern": "import requests",
                    "page": 1,
                    "per_page": 1,
                }
            ),
            content_type="application/json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)
        self.assertEqual(len(data["matches"]), 1)

    @patch("gistapi.gistapi.requests.get")
    def test_search_with_pagination_second_page(self, mock_get):
        """Test the search endpoint with pagination, second page."""
        mock_get.side_effect = self.mock_gists_response

        response = self.app.post(
            "/api/v1/search",
            data=json.dumps(
                {
                    "username": "justdionysus",
                    "pattern": "import requests",
                    "page": 2,
                    "per_page": 1,
                }
            ),
            content_type="application/json",
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("matches", data)
        self.assertIsInstance(data["matches"], list)
        self.assertEqual(len(data["matches"]), 1)


if __name__ == "__main__":
    unittest.main()

