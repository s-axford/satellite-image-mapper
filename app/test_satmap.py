import os
import io
from satmap import app
from satmap import generate_overlay_image
import unittest

# Test API calls
class FlaskTestCase(unittest.TestCase):

    # adds flask app to TestCase
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    # ensures homepage is provided
    def test_home(self):
        response = self.app.get('/')
        # Make sure valid request returns success response
        self.assertEqual(response.status_code, 200)
        # Make sure html page is rendered
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    # tests post form submit with valid data
    def test_valid_form_submit(self):
        """valid form submitted"""
        data = {'lat': 45, 'long': -79}
        data = {key: str(value) for key, value in data.items()}
        f = open(
            os.path.join(
                os.path.dirname(__file__),
                'static/images/',
                "plume.png"),
            'rb')
        buffer = io.BytesIO(f.read())
        data['file'] = (buffer, 'test.png')
        f.close()
        response = self.app.post(
            '/', data=data,
            content_type='multipart/form-data'
        )
        buffer.close()
        # Make sure valid request returns success response
        self.assertEqual(response.status_code, 200)
        # Make sure html page is rendered
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        response.close()

    # tests valid API GET request
    def test_valid_file_upload(self):
        """valid test file uploaded"""
        data = {'lat': 45, 'long': -79}
        data = {key: str(value) for key, value in data.items()}
        f = open(
            os.path.join(
                os.path.dirname(__file__),
                'static/images/',
                "plume.png"),
            'rb')
        buffer = io.BytesIO(f.read())
        data['file'] = (buffer, 'test.png')
        f.close()
        response = self.app.get(
            '/satmap/api/v1.0/generate', data=data,
            content_type='multipart/form-data'
        )
        buffer.close()
        # ensure valid request returns success response
        self.assertEqual(response.status_code, 200)
        # ensure a png image was returned
        self.assertEqual(response.content_type, "image/png")
        response.close()

    # tests invalid API GET request when file is invalid type
    def test_invalid_file_upload(self):
        """invalid test file uploaded"""
        data = {'lat': 45, 'long': -79}
        data = {key: str(value) for key, value in data.items()}
        buffer = io.BytesIO(b"abcdef")
        data['file'] = (buffer, 'test.txt')
        response = self.app.get(
            '/satmap/api/v1.0/generate', data=data,
            content_type='multipart/form-data'
        )
        buffer.close()
        # ensure proper error was returned
        self.assertEqual(response.data, b'{\n  "error": "File Not Valid"\n}\n')
        # ensure valid request returns success response
        self.assertEqual(response.status_code, 200)
        response.close()

    # tests invalid API GET request when no file is provided
    def test_no_file_upload(self):
        """no test file uploaded"""
        data = {'lat': 45, 'long': -79}
        data = {key: str(value) for key, value in data.items()}
        response = self.app.get(
            '/satmap/api/v1.0/generate', data=data,
            content_type='multipart/form-data'
        )
        # ensure proper error was returned
        self.assertEqual(response.data, b'{\n  "error": "No File Attached"\n}\n')
        # esure valid request returns success response
        self.assertEqual(response.status_code, 200)
        response.close()

    # tests invalid API GET request when no cordinates are incorrect
    def test_invalid_cordinates_upload(self):
        """no test file uploaded"""
        # check incorrect longitude
        data = {'lat': 90, 'long': -300}
        data = {key: str(value) for key, value in data.items()}
        response = self.app.get(
            '/satmap/api/v1.0/generate', data=data,
            content_type='multipart/form-data'
        )
        # ensure proper error was returned
        self.assertEqual(response.data,  b'{\n  "error": "Cordinates Not Valid"\n}\n')
        # esure valid request returns success response
        self.assertEqual(response.status_code, 200)
        response.close()
        # check incorrect latitude
        data = {'lat': 400, 'long': -10}
        data = {key: str(value) for key, value in data.items()}
        response = self.app.get(
            '/satmap/api/v1.0/generate', data=data,
            content_type='multipart/form-data'
        )
        # ensure proper error was returned
        self.assertEqual(response.data,  b'{\n  "error": "Cordinates Not Valid"\n}\n')
        # esure valid request returns success response
        self.assertEqual(response.status_code, 200)
        response.close()

if __name__ == "__main__":
    unittest.main()
