import sys
import os
import unittest
from unittest.mock import patch, Mock
import requests

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from petfinder import api_query_response, chosen_post_data

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.mockData = ""

    @patch('petfinder.requests.request')
    def test_correct_API_query_response(self, mock_request):
        mock_response = Mock()
        expected_data = {
            "pets": [
                {
                    "pet_id": "1",
                    "pet_name": "Buddy",
                    "primary_breed": "Labrador",
                    "secondary_breed": "None",
                    "sex": "M",
                    "age": "Young",
                    "size": "Medium",
                    "results_photo_url": "http://example.com/photo.jpg"
                }
            ]
        }
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        result = api_query_response('02115', '10', 'M', 'young', False)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['pet_id'], "1")
        self.assertEqual(result[0]['pet_name'], "Buddy")
        self.assertEqual(result[0]['primary_breed'], "Labrador")
        self.assertEqual(result[0]['photo_link'], "http://example.com/photo.jpg")

    @patch('petfinder.requests.request')
    def test_correct_chosen_post_data(self, mock_request):
        # Define the mock response data
        mock_response = Mock()
        expected_data = {
            "pet": {
                "pet_id": "1",
                "pet_name": "Buddy",
                "primary_breed": "Labrador",
                "secondary_breed": "None",
                "sex": "M",
                "age": "Young",
                "size": "Medium",
                "results_photo_url": "http://example.com/photo.jpg"
            }
        }
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response

        # Call the function
        result = chosen_post_data("1")

        # Check the result
        self.assertEqual(result['pet_id'], "1")
        self.assertEqual(result['pet_name'], "Buddy")
        self.assertEqual(result['primary_breed'], "Labrador")
        self.assertEqual(result['results_photo_url'], "http://example.com/photo.jpg")

if __name__ == '__main__':
    unittest.main()
