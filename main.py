"""
German Exam Registration Bot - Main Application
"""
import sys
import json
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging
from de_exam_bot.driver_manager import DriverManager
from de_exam_bot.config import Config
from de_exam_bot.processing import ContentProcessor, ProcessedContent

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/exam_bot.log'),
            logging.StreamHandler()
        ]
    )

def test_content_processor(driver, url: str):
    """Test the ContentProcessor functionality"""
    print(f"\n🔍 Testing ContentProcessor on: {url}")
    print("-" * 50)
    
    try:
        # Initialize ContentProcessor with default config
        processor = ContentProcessor()
        
        # Navigate to the URL
        driver.get(url)
        print(f"✅ Loaded page: {driver.title}")
        
        # Process the page content
        print("🔄 Processing page content...")
        processed_content = processor.process_page(driver)
        
        # Display results
        print("\n📊 Processing Results:")
        print(f"Timestamp: {processed_content.timestamp}")
        
        # Raw content info
        if processed_content.raw:
            print(f"Raw content keys: {list(processed_content.raw.keys())}")
            if 'title' in processed_content.raw:
                print(f"Page title: {processed_content.raw['title']}")
            if 'url' in processed_content.raw:
                print(f"URL: {processed_content.raw['url']}")
            if 'full_html' in processed_content.raw:
                print(f"HTML Code (First 100 characters): {processed_content.raw['full_html'][:100]}")
            if 'body_text' in processed_content.raw:
                print(f"Body Text (First 100 characters): {processed_content.raw['body_text'][:100]}")
        
        # 🔥 STRUCTURED DATA TESTING 🔥
        print("\n📊 Testing Structured Data Extraction:")
        print("-" * 40)
        
        if hasattr(processed_content, 'structured') and processed_content.structured:
            # Test Forms
            forms = processed_content.structured.get('forms', [])
            print(f"📝 Forms found: {len(forms)}")
            for i, form in enumerate(forms[:3]):  # Show first 3 forms
                if 'error' not in form:
                    print(f"  Form {i}: {form.get('method', 'GET')} {form.get('action', 'no-action')}")
                    print(f"    ID: {form.get('id', 'no-id')}")
                    print(f"    Inputs: {form.get('inputs_count', 0)}, Buttons: {form.get('buttons_count', 0)}")
                    print(f"    Visible: {form.get('is_visible', False)}")
                    if form.get('text_content'):
                        print(f"    Text: {form['text_content'][:50]}...")
                else:
                    print(f"  Form {i}: ❌ {form.get('error', 'unknown error')}")
            
            # Test Buttons  
            buttons = processed_content.structured.get('buttons', [])
            print(f"\n🔘 Buttons found: {len(buttons)}")
            for i, button in enumerate(buttons[:5]):  # Show first 5 buttons
                if 'error' not in button:
                    print(f"  Button {i}: '{button.get('text', 'no-text')}' ({button.get('tag', 'unknown')})")
                    print(f"    Type: {button.get('type', 'no-type')}")
                    print(f"    ID: {button.get('id', 'no-id')}")
                    print(f"    Visible: {button.get('is_visible', False)}, Enabled: {button.get('is_enabled', False)}")
                else:
                    print(f"  Button {i}: ❌ {button.get('error', 'unknown error')}")
            
            # Test Links
            links = processed_content.structured.get('links', {})
            if 'error' not in links:
                print(f"\n🔗 Links Summary:")
                print(f"  Total links: {links.get('total_count', 0)}")
                print(f"  Links with href: {links.get('with_href', 0)}")
                print(f"  External links: {links.get('external_links', 0)}")
                
                reg_links = links.get('registration_links', [])
                print(f"  Registration-related links: {len(reg_links)}")
                for i, link in enumerate(reg_links[:3]):  # Show first 3 registration links
                    print(f"    {i+1}. '{link.get('text', 'no-text')}' → {link.get('href', 'no-href')[:50]}...")
            else:
                print(f"🔗 Links: ❌ {links.get('error', 'unknown error')}")
                
        else:
            print("❌ No structured data found")
        
        # Test Overall Structure
        print(f"\n📈 Structured Data Summary:")
        if hasattr(processed_content, 'structured'):
            print(f"Structured data keys: {list(processed_content.structured.keys())}")
            total_elements = 0
            if 'forms' in processed_content.structured:
                total_elements += len(processed_content.structured['forms'])
            if 'buttons' in processed_content.structured:
                total_elements += len(processed_content.structured['buttons'])
            if 'links' in processed_content.structured and 'total_count' in processed_content.structured['links']:
                total_elements += processed_content.structured['links']['total_count']
            print(f"Total interactive elements found: {total_elements}")
        else:
            print("❌ No structured data attribute found")
        
        # Check for errors
        if 'error' in processed_content.raw:
            print(f"❌ Error in processing: {processed_content.raw['error']}")
        else:
            print("✅ Content processing completed successfully")
        
        # 💾 SAVE STRUCTURED DATA TO ORGANIZED FOLDERS 💾
        print("\n💾 Saving structured data to organized folders...")
        
        # Create website-specific folder
        domain = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_')
        data_folder = Path('data') / domain
        data_folder.mkdir(parents=True, exist_ok=True)
        
        if processed_content.raw and hasattr(processed_content, 'structured'):
            # Save HTML
            html_file = data_folder / 'page.html'
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(processed_content.raw.get('full_html', ''))
            print(f"📄 HTML saved to: {html_file}")
            
            # Save Body Text
            text_file = data_folder / 'body_text.txt'
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(processed_content.raw.get('body_text', ''))
            print(f"📝 Body text saved to: {text_file}")
            
            # Save Forms Data
            forms = processed_content.structured.get('forms', [])
            if forms:
                forms_file = data_folder / 'forms.json'
                with open(forms_file, "w", encoding="utf-8") as file:
                    json.dump(forms, file, indent=2, ensure_ascii=False)
                print(f"📝 Forms data ({len(forms)} forms) saved to: {forms_file}")
            
            # Save Buttons Data  
            buttons = processed_content.structured.get('buttons', [])
            if buttons:
                buttons_file = data_folder / 'buttons.json'
                with open(buttons_file, "w", encoding="utf-8") as file:
                    json.dump(buttons, file, indent=2, ensure_ascii=False)
                print(f"🔘 Buttons data ({len(buttons)} buttons) saved to: {buttons_file}")
            
            # Save Links Data
            links = processed_content.structured.get('links', {})
            if links and 'error' not in links:
                links_file = data_folder / 'links.json'
                with open(links_file, "w", encoding="utf-8") as file:
                    json.dump(links, file, indent=2, ensure_ascii=False)
                print(f"🔗 Links data ({links.get('total_count', 0)} links) saved to: {links_file}")
            
            # Save Complete Structured Data
            structured_file = data_folder / 'structured_data.json'
            with open(structured_file, "w", encoding="utf-8") as file:
                json.dump(processed_content.structured, file, indent=2, ensure_ascii=False)
            print(f"📊 Complete structured data saved to: {structured_file}")
            
            # Save Summary
            raw_summary = {
                'url': processed_content.raw.get('url', ''),
                'title': processed_content.raw.get('title', ''),
                'timestamp': str(processed_content.timestamp),
                'content_lengths': {
                    'html_chars': len(processed_content.raw.get('full_html', '')),
                    'text_chars': len(processed_content.raw.get('body_text', '')),
                    'forms_found': len(forms),
                    'buttons_found': len(buttons),
                    'links_found': links.get('total_count', 0) if links else 0
                }
            }
            summary_file = data_folder / 'summary.json'
            with open(summary_file, "w", encoding="utf-8") as file:
                json.dump(raw_summary, file, indent=2, ensure_ascii=False)
            print(f"📋 Summary saved to: {summary_file}")
            
            print(f"✅ All data saved to folder: {data_folder}")
            
        else:
            print("❌ No data to save")
        
        return processed_content
        
    except Exception as e:
        print(f"❌ Error testing ContentProcessor: {e}")
        return None

def main():
    """Main application entry point"""
    setup_logging()
    
    print("🎯 German Exam Registration Bot - ContentProcessor Test")
    print("=" * 60)
    
    config = Config()
    dm = DriverManager()
    
    try:
        print(f"Using browser: {config.default_browser}")
        driver = dm.get_driver()
        print("✅ WebDriver initialized successfully")
        
        # Test URLs for German exam websites
        test_urls = [
            "https://www.goethe.de",
            "https://academieallemande.ma/announcements",
        ]
        
        for url in test_urls:
            try:
                processed_content = test_content_processor(driver, url)
                
                if processed_content:
                    print(f"\n📈 Processing Summary for {url}:")
                    print(f"- Raw data fields: {len(processed_content.raw)}")
                    
                    # Show first 100 characters of HTML if available
                    if 'full_html' in processed_content.raw:
                        html_preview = processed_content.raw['full_html'][:100] + "..." if len(processed_content.raw['full_html']) > 100 else processed_content.raw['full_html']
                        print(f"- HTML preview: {html_preview}")
                
                print("\n" + "="*60)
                
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")
                continue
        
        print("\n🎉 ContentProcessor testing completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Testing stopped by user (Ctrl+C)")
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    finally:
        try:
            dm.close_driver()
            print("🧹 Cleanup completed")
        except Exception:
            print("🧹 Cleanup completed (with minor issues)")

if __name__ == "__main__":
    main()