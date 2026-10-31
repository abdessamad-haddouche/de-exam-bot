import os
<<<<<<< HEAD
import requests
import zipfile
import shutil
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
=======
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

import platform
import logging
>>>>>>> 2cdb6f8 (Last changes)
from typing import Optional
from .config import Config

class DriverManager:
<<<<<<< HEAD
    """Manages WebDriver setup for Windows browsers"""
=======
    """Manages WebDriver setup for multiple browsers with automatic driver downloads"""
>>>>>>> 2cdb6f8 (Last changes)
    
    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
        self.config = Config()
<<<<<<< HEAD
        self.supported_browsers = ['chrome', 'firefox']
        
    def get_driver(self, browser: Optional[str] = None, headless: Optional[bool] = None, stealth: bool = False) -> webdriver.Remote:
        """Get WebDriver for Windows browsers"""
=======
        self.supported_browsers = ['chrome', 'firefox', 'edge']
        
    def get_driver(self, browser: Optional[str] = None, headless: Optional[bool] = None, stealth: bool = False) -> webdriver.Remote:
        """
        Get WebDriver for specified browser with config integration
        
        Args:
            browser (str, optional): Browser name. Defaults to config setting.
            headless (bool, optional): Run in headless mode. Defaults to config setting.
            stealth (bool): Enable anti-detection features
        
        Returns:
            WebDriver: Configured browser driver
        """
        # Use config defaults if not specified
>>>>>>> 2cdb6f8 (Last changes)
        browser = browser or self.config.default_browser
        headless = headless if headless is not None else self.config.headless_mode
        
        browser = browser.lower()
        
        if browser not in self.supported_browsers:
<<<<<<< HEAD
            raise ValueError(f"Browser '{browser}' not supported. Available: {self.supported_browsers}")
=======
            raise ValueError(f"Browser '{browser}' not supported. Use: {self.supported_browsers}")
>>>>>>> 2cdb6f8 (Last changes)
        
        if browser == 'chrome':
            return self._get_chrome_driver(headless, stealth)
        elif browser == 'firefox':
            return self._get_firefox_driver(headless, stealth)
<<<<<<< HEAD
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    def _get_chrome_driver(self, headless: bool = False, stealth: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver for Windows with proper error handling"""
        options = ChromeOptions()
        
=======
        elif browser == 'edge':
            return self._get_edge_driver(headless, stealth)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    def _get_chrome_driver(self, headless: bool = True, stealth: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver with config integration - CROSS PLATFORM"""
        import platform
        import requests
        import zipfile
        import stat
        from pathlib import Path
        
        options = ChromeOptions()
        
        # Detect platform and set Chrome path
        system = platform.system().lower()
        if system == "linux" and Path("/mnt/c").exists():  # WSL
            options.binary_location = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
            driver_name = 'chromedriver.exe'
            download_url = 'https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.96/win64/chromedriver-win64.zip'
            extract_folder = 'chromedriver-win64'
        elif system == "windows":  # Native Windows
            # Chrome auto-detected by Selenium on Windows
            driver_name = 'chromedriver.exe'
            download_url = 'https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.96/win64/chromedriver-win64.zip'
            extract_folder = 'chromedriver-win64'
        else:  # Linux native
            driver_name = 'chromedriver'
            download_url = 'https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.96/linux64/chromedriver-linux64.zip'
            extract_folder = 'chromedriver-linux64'
        
>>>>>>> 2cdb6f8 (Last changes)
        # Basic options
        if headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Window size from config
        window_size = self.config.data['browser_defaults']['window_size']
        options.add_argument(f'--window-size={window_size["width"]},{window_size["height"]}')
        
<<<<<<< HEAD
        # Anti-detection options
        if stealth or self.config.data['browser_defaults']['stealth_mode']:
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        # Windows ChromeDriver setup with proper handling
        driver_dir = Path(self.config.get_driver_cache_path('chrome'))
        driver_path = driver_dir / 'chromedriver.exe'
        
        # Check if driver exists and is valid
        if self._is_driver_valid(driver_path):
            print("✅ Using existing ChromeDriver")
            service = ChromeService(str(driver_path))
            driver = webdriver.Chrome(service=service, options=options)
            self.driver = driver
            return driver
        
        # Download/update driver
        print("📥 Downloading/updating ChromeDriver for Windows...")
        
        # Clean up any existing files
        if driver_dir.exists():
            shutil.rmtree(driver_dir, ignore_errors=True)
        
        driver_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            url = 'https://storage.googleapis.com/chrome-for-testing-public/144.0.7559.96/win64/chromedriver-win64.zip'
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
=======
        # Setup driver directory
        driver_dir = Path.home() / f'chromedriver_{system}'
        driver_dir.mkdir(exist_ok=True)
        driver_path = driver_dir / driver_name
        
        # Download and setup driver if not exists
        if not driver_path.exists():
            print(f"📥 Downloading ChromeDriver for {system}...")
            
            response = requests.get(download_url)
>>>>>>> 2cdb6f8 (Last changes)
            zip_path = driver_dir / 'chromedriver.zip'
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
<<<<<<< HEAD
            # Move the executable
            extracted_path = driver_dir / 'chromedriver-win64' / 'chromedriver.exe'
            if extracted_path.exists():
                extracted_path.rename(driver_path)
                
                # Clean up
                zip_path.unlink(missing_ok=True)
                shutil.rmtree(driver_dir / 'chromedriver-win64', ignore_errors=True)
                
                print("✅ ChromeDriver installed successfully!")
            else:
                raise FileNotFoundError("ChromeDriver executable not found in downloaded zip")
                
        except Exception as e:
            print(f"❌ Failed to download ChromeDriver: {e}")
            raise
        
        service = ChromeService(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)
        
        if stealth or self.config.data['browser_defaults']['stealth_mode']:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver = driver
        return driver

    def _is_driver_valid(self, driver_path: Path) -> bool:
        """Check if existing driver is valid and up-to-date"""
        if not driver_path.exists():
            return False
        
        try:
            # Try to get version
            result = subprocess.run([str(driver_path), '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and '144.0.7559' in result.stdout:
                return True
        except:
            pass
        
        return False
    
    def _get_firefox_driver(self, headless: bool = False, stealth: bool = False) -> webdriver.Firefox:
        """Setup Firefox driver for Windows"""
=======
            # Move the executable to correct location
            extracted_path = driver_dir / extract_folder / driver_name
            extracted_path.rename(driver_path)
            
            # Set executable permissions (works on all platforms)
            driver_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            # Cleanup
            zip_path.unlink()
            (driver_dir / extract_folder).rmdir()
            
            print(f"✅ ChromeDriver downloaded and configured for {system}!")
        
        service = ChromeService(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)
        self.driver = driver
        return driver
    
    def _get_firefox_driver(self, headless: bool = True, stealth: bool = False) -> webdriver.Firefox:
        """Setup Firefox driver with config integration"""
>>>>>>> 2cdb6f8 (Last changes)
        options = FirefoxOptions()
        
        if headless:
            options.add_argument('--headless')
        
<<<<<<< HEAD
=======
        # Window size from config
>>>>>>> 2cdb6f8 (Last changes)
        window_size = self.config.data['browser_defaults']['window_size']
        options.add_argument(f'--width={window_size["width"]}')
        options.add_argument(f'--height={window_size["height"]}')
        
<<<<<<< HEAD
=======
        # Anti-detection options
>>>>>>> 2cdb6f8 (Last changes)
        if stealth or self.config.data['browser_defaults']['stealth_mode']:
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0")
        
<<<<<<< HEAD
        cache_path = self.config.get_driver_cache_path('firefox')
        os.environ['WDM_LOCAL_CACHE'] = cache_path
        
        service = FirefoxService(GeckoDriverManager().install())
=======
        # Set cache path via environment variable
        cache_path = self.config.get_driver_cache_path('firefox')
        os.environ['WDM_LOCAL_CACHE'] = cache_path
        
        # Use GeckoDriverManager without path parameter
        service = FirefoxService(GeckoDriverManager().install())
        
>>>>>>> 2cdb6f8 (Last changes)
        driver = webdriver.Firefox(service=service, options=options)
        self.driver = driver
        return driver
    
<<<<<<< HEAD
    def close_driver(self) -> None:
        """Close the current driver with proper error handling"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                # Silently ignore errors during cleanup
                # Browser may have already closed or connection lost
                pass
            finally:
                self.driver = None
    
    def get_available_browsers(self) -> list[str]:
        """Get list of available Windows browsers"""
        return self.supported_browsers
=======
    def _get_edge_driver(self, headless: bool = True, stealth: bool = False) -> webdriver.Edge:
        """Setup Edge driver with config integration"""
        options = EdgeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Performance options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Window size from config
        window_size = self.config.data['browser_defaults']['window_size']
        options.add_argument(f'--window-size={window_size["width"]},{window_size["height"]}')
        
        # Anti-detection options
        if stealth or self.config.data['browser_defaults']['stealth_mode']:
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Set cache path via environment variable
        cache_path = self.config.get_driver_cache_path('edge')
        os.environ['WDM_LOCAL_CACHE'] = cache_path
        
        # Use EdgeChromiumDriverManager without path parameter
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        driver = webdriver.Edge(service=service, options=options)
        self.driver = driver
        return driver
    
    def close_driver(self) -> None:
        """Close the current driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_available_browsers(self) -> list[str]:
        """Get list of browsers available on current platform"""
        available = ['chrome', 'firefox', 'edge']
        
        if platform.system() == 'Darwin':
            available.append('safari')
        
        return available
>>>>>>> 2cdb6f8 (Last changes)
