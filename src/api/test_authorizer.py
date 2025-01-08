import unittest
from unittest.mock import patch, MagicMock
from authorizer import lambda_handler

class TestAuthorizer(unittest.TestCase):

    @patch('authorizer.validate_jwt')
    @patch('authorizer.generate_customer_policy')
    @patch('authorizer.generate_basic_policy')
    def test_lambda_handler_admin(self, mock_generate_basic_policy, mock_generate_customer_policy, mock_validate_jwt):
        # Mock the return values
        mock_validate_jwt.return_value = {
            "sub": "user123",
            "cognito:groups": ["Admins"],
            "exp": 9999999999,
            "aud": "your_app_client_id"
        }
        mock_generate_customer_policy.return_value = {"policy": "mocked_admin_policy"}

        event = {
            "authorizationToken": "Bearer valid_token",
            "methodArn": "arn:aws:execute-api:region:account_id:api_id/stage/GET/resource"
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assertions to ensure the correct policy is returned for an admin
        self.assertEqual(result, {"policy": "mocked_admin_policy"})
        mock_validate_jwt.assert_called_once_with("Bearer valid_token")
        mock_generate_customer_policy.assert_called_once_with("user123", "Allow", event["methodArn"])

    @patch('authorizer.validate_jwt')
    @patch('authorizer.generate_customer_policy')
    @patch('authorizer.generate_basic_policy')
    def test_lambda_handler_customer(self, mock_generate_basic_policy, mock_generate_customer_policy, mock_validate_jwt):
        # Mock the return values
        mock_validate_jwt.return_value = {
            "sub": "user123",
            "cognito:groups": ["Customers"],
            "exp": 9999999999,
            "aud": "your_app_client_id"
        }
        mock_generate_customer_policy.return_value = {"policy": "mocked_customer_policy"}

        event = {
            "authorizationToken": "Bearer valid_token",
            "methodArn": "arn:aws:execute-api:region:account_id:api_id/stage/GET/resource"
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assertions to ensure the correct policy is returned for a customer
        self.assertEqual(result, {"policy": "mocked_customer_policy"})
        mock_validate_jwt.assert_called_once_with("Bearer valid_token")
        mock_generate_customer_policy.assert_called_once_with("user123", "Allow", event["methodArn"])

    @patch('authorizer.validate_jwt')
    @patch('authorizer.generate_customer_policy')
    @patch('authorizer.generate_basic_policy')
    def test_lambda_handler_invalid_token(self, mock_generate_basic_policy, mock_generate_customer_policy, mock_validate_jwt):
        # Mock the invalid JWT token 
        mock_validate_jwt.side_effect = Exception("Unauthorized: Token expired")

        event = {
            "authorizationToken": "Bearer invalid_token",
            "methodArn": "arn:aws:execute-api:region:account_id:api_id/stage/GET/resource"
        }
        context = {}

        # Call the lambda_handler function and expect an exception
        with self.assertRaises(Exception) as context_manager:
            lambda_handler(event, context)

        self.assertEqual(str(context_manager.exception), "Unauthorized")
        mock_validate_jwt.assert_called_once_with("Bearer invalid_token")

    @patch('authorizer.validate_jwt')
    @patch('authorizer.generate_customer_policy')
    @patch('authorizer.generate_basic_policy')
    def test_lambda_handler_no_group(self, mock_generate_basic_policy, mock_generate_customer_policy, mock_validate_jwt):
        # Mock the return values
        mock_validate_jwt.return_value = {
            "sub": "user123",
            "cognito:groups": [],
            "exp": 9999999999,
            "aud": "your_app_client_id"
        }
        mock_generate_basic_policy.return_value = {"policy": "mocked_deny_policy"}

        event = {
            "authorizationToken": "Bearer valid_token",
            "methodArn": "arn:aws:execute-api:region:account_id:api_id/stage/GET/resource"
        }
        context = {}

        # Call the lambda_handler function
        result = lambda_handler(event, context)

        # Assertions to ensure the correct deny policy is returned
        self.assertEqual(result, {"policy": "mocked_deny_policy"})
        mock_validate_jwt.assert_called_once_with("Bearer valid_token")
        mock_generate_basic_policy.assert_called_once_with("user123", "Deny", event["methodArn"])

if __name__ == '__main__':
    unittest.main()
