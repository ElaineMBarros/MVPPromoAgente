"""
Azure OCR Service Module
Provides OCR functionality using Azure Computer Vision API
"""
import os
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureOCRService:
    """Service class for Azure Computer Vision OCR operations"""
    
    def __init__(self, endpoint=None, key=None):
        """
        Initialize the Azure OCR Service
        
        Args:
            endpoint (str): Azure Computer Vision endpoint URL
            key (str): Azure Computer Vision subscription key
        """
        # Load environment variables
        load_dotenv()
        
        # Get credentials from parameters or environment
        self.endpoint = endpoint or os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
        self.key = key or os.getenv('AZURE_COMPUTER_VISION_KEY')
        
        if not self.endpoint or not self.key:
            raise ValueError(
                "Azure credentials not provided. Please set AZURE_COMPUTER_VISION_ENDPOINT "
                "and AZURE_COMPUTER_VISION_KEY environment variables or pass them as parameters."
            )
        
        # Initialize the Computer Vision client
        self.client = ComputerVisionClient(
            self.endpoint,
            CognitiveServicesCredentials(self.key)
        )
        logger.info("Azure OCR Service initialized successfully")
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from a local image file using OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Dictionary containing extracted text and metadata
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Check if file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read the image
            with open(image_path, "rb") as image_stream:
                # Call the Read API
                read_operation = self.client.read_in_stream(image_stream, raw=True)
            
            # Get the operation location (URL with operation ID)
            operation_location = read_operation.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for the operation to complete
            logger.info("Waiting for OCR operation to complete...")
            while True:
                read_result = self.client.get_read_result(operation_id)
                if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                    break
                time.sleep(1)
            
            # Process results
            if read_result.status == OperationStatusCodes.succeeded:
                extracted_text = []
                text_lines = []
                
                for page in read_result.analyze_result.read_results:
                    for line in page.lines:
                        text_lines.append(line.text)
                        extracted_text.append({
                            'text': line.text,
                            'bounding_box': line.bounding_box,
                            'confidence': getattr(line, 'confidence', None)
                        })
                
                full_text = "\n".join(text_lines)
                
                result = {
                    'success': True,
                    'text': full_text,
                    'lines': extracted_text,
                    'line_count': len(text_lines)
                }
                
                logger.info(f"Successfully extracted {len(text_lines)} lines of text")
                return result
            else:
                logger.error(f"OCR operation failed with status: {read_result.status}")
                return {
                    'success': False,
                    'error': f"OCR operation failed with status: {read_result.status}"
                }
                
        except FileNotFoundError as e:
            logger.error(str(e))
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def extract_text_from_url(self, image_url):
        """
        Extract text from an image URL using OCR
        
        Args:
            image_url (str): URL of the image
            
        Returns:
            dict: Dictionary containing extracted text and metadata
        """
        try:
            logger.info(f"Processing image URL: {image_url}")
            
            # Call the Read API with URL
            read_operation = self.client.read(image_url, raw=True)
            
            # Get the operation location (URL with operation ID)
            operation_location = read_operation.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for the operation to complete
            logger.info("Waiting for OCR operation to complete...")
            while True:
                read_result = self.client.get_read_result(operation_id)
                if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                    break
                time.sleep(1)
            
            # Process results
            if read_result.status == OperationStatusCodes.succeeded:
                extracted_text = []
                text_lines = []
                
                for page in read_result.analyze_result.read_results:
                    for line in page.lines:
                        text_lines.append(line.text)
                        extracted_text.append({
                            'text': line.text,
                            'bounding_box': line.bounding_box,
                            'confidence': getattr(line, 'confidence', None)
                        })
                
                full_text = "\n".join(text_lines)
                
                result = {
                    'success': True,
                    'text': full_text,
                    'lines': extracted_text,
                    'line_count': len(text_lines)
                }
                
                logger.info(f"Successfully extracted {len(text_lines)} lines of text")
                return result
            else:
                logger.error(f"OCR operation failed with status: {read_result.status}")
                return {
                    'success': False,
                    'error': f"OCR operation failed with status: {read_result.status}"
                }
                
        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return {'success': False, 'error': str(e)}
