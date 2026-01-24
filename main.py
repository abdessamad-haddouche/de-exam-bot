"""
German Exam Registration Bot - Main Application
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging
from de_exam_bot.driver_manager import DriverManager
from de_exam_bot.config import Config

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

def main():
    """Main application entry point"""
    setup_logging()
    
    print("🎯 German Exam Registration Bot")
    print("=" * 40)
    
    config = Config()
    dm = DriverManager()
    
    try:
        print(f"Using browser: {config.default_browser}")
        driver = dm.get_driver()
        
        # Your exam monitoring logic will go here
        print("🚀 Bot ready for exam monitoring!")
        
        # Example: Navigate to a German exam website
        driver.get("https://www.goethe.de")
        print(f"📄 Loaded: {driver.title}")
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (Ctrl+C)")
        print("👋 Goodbye!")
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"❌ Error: {e}")
    finally:
        try:
            dm.close_driver()
            print("🧹 Cleanup completed")
        except:
            print("🧹 Cleanup completed (with minor issues)")

if __name__ == "__main__":
    main()