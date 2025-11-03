"""
Promotional Agent Module
Main application that uses OCR to analyze promotional materials
"""
import logging
from azure_ocr_service import AzureOCRService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PromoAgent:
    """
    Promotional Agent that analyzes promotional materials using OCR
    """
    
    def __init__(self):
        """Initialize the Promotional Agent with Azure OCR Service"""
        try:
            self.ocr_service = AzureOCRService()
            logger.info("Promotional Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Promotional Agent: {str(e)}")
            raise
    
    def analyze_promotional_image(self, image_source, is_url=False):
        """
        Analyze a promotional image and extract text information
        
        Args:
            image_source (str): Path to image file or URL
            is_url (bool): Whether the source is a URL or file path
            
        Returns:
            dict: Analysis results including extracted text and insights
        """
        logger.info(f"Analyzing promotional material: {image_source}")
        
        # Extract text using OCR
        if is_url:
            ocr_result = self.ocr_service.extract_text_from_url(image_source)
        else:
            ocr_result = self.ocr_service.extract_text_from_image(image_source)
        
        if not ocr_result['success']:
            logger.error(f"OCR extraction failed: {ocr_result.get('error', 'Unknown error')}")
            return ocr_result
        
        # Analyze extracted text
        extracted_text = ocr_result['text']
        analysis = self._analyze_text(extracted_text)
        
        # Combine OCR results with analysis
        result = {
            'success': True,
            'source': image_source,
            'extracted_text': extracted_text,
            'line_count': ocr_result['line_count'],
            'lines': ocr_result['lines'],
            'analysis': analysis
        }
        
        logger.info("Analysis completed successfully")
        return result
    
    def _analyze_text(self, text):
        """
        Analyze extracted text for promotional insights
        
        Args:
            text (str): Extracted text from promotional material
            
        Returns:
            dict: Analysis insights
        """
        # Basic text analysis
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Detect promotional keywords
        promotional_keywords = [
            'desconto', 'promoção', 'oferta', 'grátis', 'gratuito',
            'descuento', 'promoción', 'oferta', 'gratis',
            'discount', 'promotion', 'offer', 'free', 'sale',
            'preço', 'precio', 'price', '%', 'R$', '$'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in promotional_keywords if kw.lower() in text_lower]
        
        # Detect numbers (prices, percentages)
        import re
        numbers = re.findall(r'\d+[.,]?\d*', text)
        percentages = re.findall(r'\d+\s*%', text)
        prices = re.findall(r'R\$\s*\d+[.,]?\d*|\$\s*\d+[.,]?\d*', text)
        
        analysis = {
            'word_count': word_count,
            'character_count': char_count,
            'is_promotional': len(found_keywords) > 0,
            'promotional_keywords_found': found_keywords,
            'numbers_detected': numbers,
            'percentages_detected': percentages,
            'prices_detected': prices,
            'has_discount_info': any(kw in text_lower for kw in ['desconto', 'discount', 'descuento', '%'])
        }
        
        return analysis
    
    def generate_report(self, analysis_result):
        """
        Generate a formatted report from analysis results
        
        Args:
            analysis_result (dict): Results from analyze_promotional_image
            
        Returns:
            str: Formatted report
        """
        if not analysis_result.get('success'):
            return f"Error: {analysis_result.get('error', 'Unknown error')}"
        
        report = []
        report.append("=" * 60)
        report.append("PROMOTIONAL MATERIAL ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nSource: {analysis_result['source']}")
        report.append(f"Lines Detected: {analysis_result['line_count']}")
        report.append("\n" + "-" * 60)
        report.append("EXTRACTED TEXT:")
        report.append("-" * 60)
        report.append(analysis_result['extracted_text'])
        report.append("\n" + "-" * 60)
        report.append("ANALYSIS:")
        report.append("-" * 60)
        
        analysis = analysis_result['analysis']
        report.append(f"Word Count: {analysis['word_count']}")
        report.append(f"Character Count: {analysis['character_count']}")
        report.append(f"Is Promotional: {'Yes' if analysis['is_promotional'] else 'No'}")
        report.append(f"Has Discount Info: {'Yes' if analysis['has_discount_info'] else 'No'}")
        
        if analysis['promotional_keywords_found']:
            report.append(f"\nPromotional Keywords Found: {', '.join(analysis['promotional_keywords_found'])}")
        
        if analysis['prices_detected']:
            report.append(f"Prices Detected: {', '.join(analysis['prices_detected'])}")
        
        if analysis['percentages_detected']:
            report.append(f"Percentages Detected: {', '.join(analysis['percentages_detected'])}")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """
    Main function demonstrating the Promotional Agent usage
    """
    import sys
    
    print("MVPPromoAgente - Promotional Material Analyzer")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python promo_agent.py <image_path>")
        print("  python promo_agent.py <image_url> --url")
        print("\nExample:")
        print("  python promo_agent.py promotional_flyer.jpg")
        print("  python promo_agent.py https://example.com/promo.jpg --url")
        return
    
    image_source = sys.argv[1]
    is_url = '--url' in sys.argv
    
    try:
        # Initialize the agent
        agent = PromoAgent()
        
        # Analyze the promotional material
        result = agent.analyze_promotional_image(image_source, is_url=is_url)
        
        # Generate and print report
        report = agent.generate_report(result)
        print("\n" + report)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
