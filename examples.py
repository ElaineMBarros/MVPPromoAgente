"""
Example script demonstrating MVPPromoAgente usage
"""
from promo_agent import PromoAgent
from azure_ocr_service import AzureOCRService


def example_basic_ocr():
    """Example 1: Basic OCR usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic OCR Usage")
    print("=" * 60)
    
    try:
        # Initialize the OCR service
        ocr_service = AzureOCRService()
        
        # Example with a URL (you can replace with your own image URL)
        image_url = "https://example.com/sample-image.jpg"
        
        print(f"\nExtracting text from URL: {image_url}")
        result = ocr_service.extract_text_from_url(image_url)
        
        if result['success']:
            print(f"\n✓ Success!")
            print(f"Extracted text:\n{result['text']}")
            print(f"\nTotal lines detected: {result['line_count']}")
        else:
            print(f"\n✗ Error: {result['error']}")
    
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")


def example_promotional_analysis():
    """Example 2: Full promotional material analysis"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Promotional Material Analysis")
    print("=" * 60)
    
    try:
        # Initialize the promotional agent
        agent = PromoAgent()
        
        # Example with a local file (replace with your image path)
        image_path = "sample_promo.jpg"
        
        print(f"\nAnalyzing promotional image: {image_path}")
        result = agent.analyze_promotional_image(image_path)
        
        # Generate and display report
        report = agent.generate_report(result)
        print("\n" + report)
    
    except FileNotFoundError:
        print(f"\n✗ Image file not found. Please provide a valid image path.")
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")


def example_url_analysis():
    """Example 3: Analyze promotional image from URL"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: URL Analysis")
    print("=" * 60)
    
    try:
        # Initialize the promotional agent
        agent = PromoAgent()
        
        # Example URL (replace with actual promotional image URL)
        image_url = "https://example.com/promotional-banner.jpg"
        
        print(f"\nAnalyzing promotional URL: {image_url}")
        result = agent.analyze_promotional_image(image_url, is_url=True)
        
        if result['success']:
            print(f"\n✓ Analysis complete!")
            print(f"Extracted text: {result['extracted_text'][:100]}...")
            print(f"Is promotional: {result['analysis']['is_promotional']}")
            print(f"Keywords found: {result['analysis']['promotional_keywords_found']}")
        else:
            print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MVPPromoAgente - Usage Examples")
    print("=" * 60)
    print("\nNote: These examples require valid Azure credentials")
    print("and appropriate image files/URLs to work properly.")
    print("\nMake sure to:")
    print("1. Set up your .env file with Azure credentials")
    print("2. Replace example URLs and paths with real ones")
    print("=" * 60)
    
    # Uncomment the examples you want to run
    # example_basic_ocr()
    # example_promotional_analysis()
    # example_url_analysis()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
