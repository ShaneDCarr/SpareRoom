import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from open_unit import lambda_handler, get_unit, switch_openness, update_unit, log_notification

class TestLambdaHandler(unittest.TestCase):
    
    @patch('open_unit.dynamo')
    def test_get_unit_success(self, mock_dynamo):
        # Setup mock response for DynamoDB query
        mock_query_response = {
            'Items': [
                {
                    'id': {'S': 'unit123'},
                    'information': {
                        'M': {
                            'details': {
                                'M': {
                                    'is_open': {'BOOL': False}
                                }
                            }
                        }
                    }
                }
            ]
        }
        mock_dynamo.query.return_value = mock_query_response
        
        # Test get_unit function
        unit = get_unit('unit123')
        
        self.assertEqual(unit['id']['S'], 'unit123')
        self.assertEqual(unit['information']['M']['details']['M']['is_open']['BOOL'], False)
    
    @patch('open_unit.dynamo')
    def test_get_unit_not_found(self, mock_dynamo):
        # Simulate a scenario where the unit is not found
        mock_dynamo.query.return_value = {'Items': []}
        
        # Test that get_unit raises an IndexError if unit is not found
        with self.assertRaises(IndexError):
            get_unit('non_existent_unit')
    
    def test_switch_openness(self):
        # Test the switch_openness function
        unit_open = {
            'information': {
                'M': {
                    'details': {
                        'M': {
                            'is_open': {'BOOL': True}
                        }
                    }
                }
            }
        }
        self.assertFalse(switch_openness(unit_open))
        
        unit_closed = {
            'information': {
                'M': {
                    'details': {
                        'M': {
                            'is_open': {'BOOL': False}
                        }
                    }
                }
            }
        }
        self.assertTrue(switch_openness(unit_closed))
    
    @patch('open_unit.dynamo')
    def test_update_unit(self, mock_dynamo):
        # Mock the response for the update_item call
        mock_dynamo.update_item.return_value = {
            'Attributes': {
                'information': {
                    'M': {
                        'details': {
                            'M': {
                                'is_open': {'BOOL': True}
                            }
                        }
                    }
                }
            }
        }
        
        unit = {'id': {'S': 'unit123'}}
        openness = True
        
        # Test the update_unit function
        response = update_unit(unit, openness)
        
        self.assertEqual(response['Attributes']['information']['M']['details']['M']['is_open']['BOOL'], True)
    
    @patch('open_unit.dynamo')
    def test_log_notification_success(self, mock_dynamo):
        # Mock update_item for logging notification
        mock_dynamo.update_item.return_value = {}
        
        # Test logging notifications
        log_notification('unit123', 'test_client@example.com', 'Opened')
        
        # Check if update_item was called
        mock_dynamo.update_item.assert_called_once()

    @patch('open_unit.dynamo')
    def test_log_notification_error(self, mock_dynamo):
        # Simulate an error during the logging process
        mock_dynamo.update_item.side_effect = Exception("Error")
        
        # Test that log_notification handles errors
        log_notification('unit123', 'test_client@example.com', 'Opened')
    
    @patch('open_unit.dynamo')
    def test_lambda_handler_success(self, mock_dynamo):
        # Mock the functions
        mock_dynamo.query.return_value = {
            'Items': [
                {
                    'id': {'S': 'unit123'},
                    'information': {
                        'M': {
                            'details': {
                                'M': {
                                    'is_open': {'BOOL': False}
                                }
                            }
                        }
                    }
                }
            ]
        }
        mock_dynamo.update_item.return_value = {}

        event = {
            'client': 'test_client@example.com',
            'unit_id': 'unit123'
        }

        # Test the lambda_handler function
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('Opened', json.loads(result['body'])['Message'])
    
    @patch('open_unit.dynamo')
    def test_lambda_handler_unit_not_found(self, mock_dynamo):
        # Mock DynamoDB query to return no items
        mock_dynamo.query.return_value = {'Items': []}
        
        event = {
            'client': 'test_client@example.com',
            'unit_id': 'non_existent_unit'
        }

        # Test the lambda_handler when unit is not found
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 400)
        self.assertIn('Item not found', json.loads(result['body'])['Message'])

    @patch('open_unit.dynamo')
    def test_lambda_handler_missing_key(self, mock_dynamo):
        # Mock DynamoDB query
        mock_dynamo.query.return_value = {
            'Items': [
                {
                    'id': {'S': 'unit123'},
                    'information': {
                        'M': {
                            'details': {
                                'M': {
                                    'is_open': {'BOOL': True}
                                }
                            }
                        }
                    }
                }
            ]
        }

        event = {
            'client': 'test_client@example.com'
            # Missing 'unit_id' key
        }

        # Test lambda_handler when there is a missing key
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 400)
        self.assertIn('Missing field', json.loads(result['body'])['Message'])

    @patch('open_unit.dynamo')
    def test_lambda_handler_invalid_type(self, mock_dynamo):
        # Simulate event with invalid type in query parameters
        event = {
            'queryStringParameters': {
                'type': 'invalid_type'
            }
        }

        # Test handler with invalid type
        result = lambda_handler(event, None)
        
        self.assertEqual(result['statusCode'], 400)
        self.assertIn("Missing field: 'client'", json.loads(result['body'])['Message'])

if __name__ == '__main__':
    unittest.main()
