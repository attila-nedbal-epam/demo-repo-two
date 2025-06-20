import unittest
from unittest.mock import patch, Mock
import json
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from weather_datetime_api import app, WeatherService, DateTimeService, Config

class TestWeatherDatetimeAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check_success(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'ok')
        self.assertIn(data['message'], 'Weather Datetime API is running')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
    
    def test_index_endpoint(self):
        """Test index endpoint with API documentation"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], 'Weather Datetime API')
        self.assertIn('endpoints', data)
        self.assertIn('examples', data)
    
    def test_datetime_endpoint_success(self):
        """Test datetime endpoint success"""
        response = self.app.get('/api/datetime')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        
        # Check datetime data structure
        datetime_data = data['data']
        self.assertIn('current_datetime_utc', datetime_data)
        self.assertIn('current_datetime_local', datetime_data)
        self.assertIn('timestamp', datetime_data)
        self.assertIn('timezone', datetime_data)
    
    @patch('src.weather_datetime_api.requests')
    def test_weather_endpoint_success(self, mock_requests):
        """Test weather endpoint success"""
        # Mock weather API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {
                'temp': 22.5,
                'feels_like': 23.0,
                'humidity': 65,
                'pressure': 1013
            },
            'weather': [{'description': 'clear sky'}],
            'wind': {'speed': 3.5, 'deg': 230},
            'clouds': {'all': 10},
            'visibility': 10000,
            'name': 'Budapest',
            'sys': {'country': 'HU'}
        }
        mock_requests.get.return_value = mock_response
        
        # Mock environment variable
        with patch.object(Config, 'OPENWEATHER_API_KEY', 'test_api_key') as mock_key:
            response = self.app.get('/api/weather')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['status'], 'success')
            self.assertIn('data', data)
            
            # Check weather data structure
            weather_data = data['data']
            self.assertEqual(weather_data['temperature'], 22.5)
            self.assertEqual(weather_data['city'], 'Budapest')
            self.assertEqual(weather_data['country'], 'HU')
    
    def test_weather_endpoint_no_api_key(self):
        """Test weather endpoint without API key"""
        with patch.object(Config, 'OPENWEATHER_API_KEY', ''):
            response = self.app.get('/api/weather')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['status'], 'success')
            self.assertIn('error', data['data'])
            self.assertIn('Weather API key not configured', data['data']['error'])
    
    @patch('src.weather_datetime_api.requests')
    def test_combined_endpoint_success(self, mock_requests):
        """Test combined endpoint success"""
        # Mock weather API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {'temp': 20.0, 'feels_like': 21.0, 'humidity': 70, 'pressure': 1015},
            'weather': [{'description': 'overcast clouds'}],
            'wind': {'speed': 2.0, 'deg': 180},
            'clouds': {'all': 90},
            'visibility': 9000,
            'name': 'Budapest',
            'sys': {'country': 'HU'}
        }
        mock_requests.get.return_value = mock_response
        
        with patch.object(Config, 'OPENWEATHER_API_KEY', 'test_api_key'):
            response = self.app.get('/api/combined')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['status'], 'success')
            self.assertIn('datetime', data)
            self.assertIn('weather', data)
            self.assertIn('location', data)
    
    def test_weather_endpoint_custom_coordinates(self):
        """Test weather endpoint with custom coordinates"""
        with patch.object(Config, 'OPENWEATHER_API_KEY', ''):
            response = self.app.get('/api/weather?lat=48.2081&lon=16.3738')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data['location']['latitude'], 48.2081)
            self.assertEqual(data['location']['longitude'], 16.3738)
    
    def test_weather_endpoint_invalid_coordinates(self):
        """Test weather endpoint with invalid coordinates"""
        response = self.app.get('/api/weather?lat=invalid&lon=also_invalid')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'error')
        self.assertIn('Invalid coordinates', data['message'])

    def test_404_error(self):
        """Test 404 error handling"""
        response = self.app.get('/api/notfound')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'error')
        self.assertIn('available_endpoints', data)

class TestWeatherService(unittest.TestCase):
    @patch('src.weather_datetime_api.requests')
    def test_get_weather_data_success(self, mock_requests):
        """Test WeatherService.get_weather_data success"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {'temp': 25.0, 'feels_like': 26.0, 'humidity': 60, 'pressure': 1020},
            'weather': [{'description': 'sunny'}],
            'wind': {'speed': 5.0, 'deg': 270},
            'clouds': {'all': 20},
            'visibility': 15000,
            'name': 'Budapest',
            'sys': {'country': 'HU'}
        }
        mock_requests.get.return_value = mock_response
        
        result = WeatherService.get_weather_data(47.4980, 19.0402, 'test_key')
        
        self.assertEqual(result['temperature'], 25.0)
        self.assertEqual(result['city'], 'Budapest')
        self.assertEqual(result['country'], 'HU')
        self.assertNotIn('error', result)
    
    def test_get_weather_data_no_api_key(self):
        """Test WeatherService.get_weather_data without API key"""
        result = WeatherService.get_weather_data(47.4980, 19.0402, '')
        
        self.assertIn('error', result)
        self.assertIn('Weather API key not configured', result['error'])
        self.assertEqual(result['temperature'], 'N/A')

class TestDateTimeService(unittest.TestCase):
    def test_get_current_datetime_success(self):
        """Test DateTimeService.get_current_datetime success"""
        result = DateTimeService.get_current_datetime()
        
        self.assertIn('current_datetime_utc', result)
        self.assertIn('current_datetime_local', result)
        self.assertIn('timestamp', result)
        self.assertIn('timezone', result)
        self.assertIsInstance(result['timestamp'], int)
        self.assertNotIn('error', result)

if __name__ == '__main__':
    unittest.main()