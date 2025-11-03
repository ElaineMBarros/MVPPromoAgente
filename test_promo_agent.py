"""
Unit tests for MVPPromoAgente
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from azure_ocr_service import AzureOCRService
from promo_agent import PromoAgent


class TestAzureOCRService(unittest.TestCase):
    """Test cases for Azure OCR Service"""
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key_12345'
    })
    @patch('azure_ocr_service.ComputerVisionClient')
    def test_service_initialization(self, mock_client):
        """Test OCR service initialization with environment variables"""
        service = AzureOCRService()
        self.assertIsNotNone(service)
        self.assertEqual(service.endpoint, 'https://test.cognitiveservices.azure.com/')
        self.assertEqual(service.key, 'test_key_12345')
    
    def test_service_initialization_without_credentials(self):
        """Test that service raises error without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AzureOCRService()
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('azure_ocr_service.ComputerVisionClient')
    def test_extract_text_file_not_found(self, mock_client):
        """Test OCR extraction with non-existent file"""
        service = AzureOCRService()
        result = service.extract_text_from_image('nonexistent_file.jpg')
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('azure_ocr_service.ComputerVisionClient')
    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_extract_text_success(self, mock_exists, mock_open, mock_client):
        """Test successful OCR text extraction"""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock file open
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock Azure client responses
        mock_instance = mock_client.return_value
        mock_read_operation = Mock()
        mock_read_operation.headers = {"Operation-Location": "https://test.com/operations/test-id-123"}
        mock_instance.read_in_stream.return_value = mock_read_operation
        
        # Mock read result
        mock_read_result = Mock()
        mock_read_result.status = 'succeeded'
        
        # Mock analyze result
        mock_line1 = Mock()
        mock_line1.text = "Test line 1"
        mock_line1.bounding_box = [0, 0, 100, 100]
        
        mock_line2 = Mock()
        mock_line2.text = "Test line 2"
        mock_line2.bounding_box = [0, 100, 100, 200]
        
        mock_page = Mock()
        mock_page.lines = [mock_line1, mock_line2]
        
        mock_analyze = Mock()
        mock_analyze.read_results = [mock_page]
        mock_read_result.analyze_result = mock_analyze
        
        mock_instance.get_read_result.return_value = mock_read_result
        
        # Test extraction
        service = AzureOCRService()
        result = service.extract_text_from_image('test_image.jpg')
        
        self.assertTrue(result['success'])
        self.assertIn('text', result)
        self.assertEqual(result['line_count'], 2)


class TestPromoAgent(unittest.TestCase):
    """Test cases for Promotional Agent"""
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('promo_agent.AzureOCRService')
    def test_agent_initialization(self, mock_ocr_service):
        """Test promotional agent initialization"""
        agent = PromoAgent()
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.ocr_service)
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('promo_agent.AzureOCRService')
    def test_analyze_text_with_promotional_keywords(self, mock_ocr_service):
        """Test text analysis with promotional keywords"""
        agent = PromoAgent()
        
        text = "MEGA PROMOÇÃO! Desconto de 50% - R$ 99,90"
        analysis = agent._analyze_text(text)
        
        self.assertTrue(analysis['is_promotional'])
        self.assertTrue(analysis['has_discount_info'])
        self.assertGreater(len(analysis['promotional_keywords_found']), 0)
        self.assertGreater(len(analysis['percentages_detected']), 0)
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('promo_agent.AzureOCRService')
    def test_analyze_text_without_promotional_keywords(self, mock_ocr_service):
        """Test text analysis without promotional keywords"""
        agent = PromoAgent()
        
        text = "This is just normal text about a meeting tomorrow at three"
        analysis = agent._analyze_text(text)
        
        self.assertFalse(analysis['is_promotional'])
        self.assertEqual(len(analysis['promotional_keywords_found']), 0)
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('promo_agent.AzureOCRService')
    def test_generate_report(self, mock_ocr_service):
        """Test report generation"""
        agent = PromoAgent()
        
        # Mock analysis result
        analysis_result = {
            'success': True,
            'source': 'test.jpg',
            'extracted_text': 'PROMOÇÃO 50%',
            'line_count': 2,
            'lines': [],
            'analysis': {
                'word_count': 2,
                'character_count': 13,
                'is_promotional': True,
                'promotional_keywords_found': ['promoção', '%'],
                'numbers_detected': ['50'],
                'percentages_detected': ['50%'],
                'prices_detected': [],
                'has_discount_info': True
            }
        }
        
        report = agent.generate_report(analysis_result)
        
        self.assertIsInstance(report, str)
        self.assertIn('PROMOTIONAL MATERIAL ANALYSIS REPORT', report)
        self.assertIn('test.jpg', report)
        self.assertIn('PROMOÇÃO 50%', report)
    
    @patch.dict(os.environ, {
        'AZURE_COMPUTER_VISION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_COMPUTER_VISION_KEY': 'test_key'
    })
    @patch('promo_agent.AzureOCRService')
    def test_generate_report_on_error(self, mock_ocr_service):
        """Test report generation with error result"""
        agent = PromoAgent()
        
        error_result = {
            'success': False,
            'error': 'Test error message'
        }
        
        report = agent.generate_report(error_result)
        
        self.assertIsInstance(report, str)
        self.assertIn('Error', report)
        self.assertIn('Test error message', report)


def run_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAzureOCRService))
    suite.addTests(loader.loadTestsFromTestCase(TestPromoAgent))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
