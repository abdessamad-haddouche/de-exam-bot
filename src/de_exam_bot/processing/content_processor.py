"""
Content Processor - Handles extraction, cleaning, and preparation of web content
"""
import re
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

@dataclass
class ProcessedContent:
    """Data class for processed web content"""
    raw: Dict[str, str]
    structured: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class ContentProcessor:
    """
    Generic content processor for German exam websites.
    Handles extraction, cleaning, and structuring for any German exam site.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with smart defaults, allow config overrides.
        
        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Start with defaults
        self.default_config = self._get_default_config()
        
        # Merge with provided config (config overrides defaults)
        self.config = config or {}
        self.final_config = {**self.default_config, **self.config}

        # Initialize from final merged config
        self.noise_patterns = self.final_config['noise_patterns']
        self.german_exam_patterns = self.final_config['german_patterns']
        self.important_selectors = self.final_config['important_selectors']
        self.processing_options = self.final_config['processing_options']
        
        # Add noise filtering control
        self.enable_noise_filtering = self.final_config.get('enable_noise_filtering', True)
        
        self.logger.info(f"ContentProcessor initialized - "
                        f"patterns: {len(self.noise_patterns)} noise, "
                        f"{len(self.german_exam_patterns)} german, "
                        f"{len(self.important_selectors)} selectors, "
                        f"noise_filtering: {'ON' if self.enable_noise_filtering else 'OFF'}")


    def _get_default_config(self) -> Dict[str, Any]:
        """Get comprehensive default configuration for German exam monitoring."""
        return {
            'noise_patterns': [
                # Date/Time patterns
                r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}', r'\d{2}\.\d{2}\.\d{4}',
                r'\d{2}:\d{2}:\d{2}', r'\d{2}:\d{2}',
                r'timestamp.*?\d+', r'last.*?updated.*?\d+',
                
                # Analytics & Tracking
                r'_ga=.*?[;&]', r'_gid=.*?[;&]', r'__utm.*?=.*?[;&]',
                r'fbclid=.*?[;&]', r'gclid=.*?[;&]',
                
                # Session Management
                r'sessionId.*?=.*?[;&]', r'PHPSESSID.*?=.*?[;&]',
                r'JSESSIONID.*?=.*?[;&]', r'ASP\.NET_SessionId.*?=.*?[;&]',
                
                # Security & Cache
                r'csrftoken.*?=.*?[;&]', r'_token.*?=.*?[;&]',
                r'cache_\w+', r'v=\d{10,}', r'_=\d{10,}', r'cb=\d+',
            ],
            'german_patterns': [
                # Registration (German)
                r'anmeldung', r'registrierung', r'einschreibung', r'buchung',
                # Registration (English)
                r'registration', r'enrollment', r'booking', r'signup',
                # Availability (German)
                r'verfügbar', r'frei', r'buchbar', r'plätze?\s+frei',
                # Availability (English)
                r'available', r'open', r'spots?\s+available',
                # Unavailable
                r'ausgebucht', r'voll', r'fully booked', r'sold out',
                # Exam specific
                r'prüfung', r'prüfungsplätze', r'exam', r'test',
                # Levels
                r'a1|a2|b1|b2|c1|c2',
                # Institutions
                r'goethe', r'ezplus', r'académie allemande', r'institut',
                # Language
                r'deutsch', r'german', r'allemand', r'deutschprüfung',
            ],
            'important_selectors': [
                # Forms & Buttons
                'form', 'button[type="submit"]', 'input[type="submit"]',
                'button[class*="register"]', 'button[class*="anmeld"]',
                # Registration sections
                '.registration', '.anmeldung', '.booking', '.buchung',
                # Availability indicators  
                '.available', '.verfügbar', '.frei', '.unavailable', '.ausgebucht',
                # Messages
                '.alert', '.warning', '.info', '.success', '.error', '.message',
                # Structure
                'h1, h2, h3', 'main', '.content',
                # Exam specific
                '.exam-date', '.prüfungstermin', '.exam-level', '.exam-location',
                # Dynamic selectors
                '[class*="register"]', '[id*="register"]', '[class*="anmeld"]',
                '[class*="exam"]', '[class*="available"]', '[class*="verfüg"]',
            ],
            'processing_options': {
                'max_elements_per_selector': 10,
                'max_text_length': 500,
                'max_matches_per_pattern': 10,
                'extract_metadata': True,
                'generate_hashes': True,
            }
        }

    def process_page(self, driver: webdriver.Remote) -> ProcessedContent:
        """
        Main entry point - processes entire page content.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            ProcessedContent object with all processed data
        """
        try:
            self.logger.debug("Processing page content...")
            
            # Step 1: Extract raw content
            raw_content = self._extract_raw_content(driver)

            # Step 2: Extract structured data
            structured_content = self._extract_structured_content(driver)
            
            return ProcessedContent(
                raw=raw_content,
                structured=structured_content,
            )
            
        except Exception as e:
            self.logger.error(f"Error processing page: {e}")
            return ProcessedContent(
                raw={'error': str(e)},
                structured={'error': str(e)},
            )

    # ===== RAW CONTENT EXTRACTION =====
    
    def _extract_raw_content(self, driver: webdriver.Remote) -> Dict[str, str]:
        """Extract raw content with configurable noise filtering."""
        try:
            raw_data = {
                'full_html': driver.page_source,
                'title': driver.title or "",
                'url': driver.current_url or "",
                'body_text': self._get_body_text(driver),
                'important_text': self._extract_important_text(driver),
                'forms_html': self._extract_forms_html(driver)
            }
            
            # Apply noise filtering based on configuration
            if self.enable_noise_filtering:
                # Define content types for smart filtering
                content_type_map = {
                    'full_html': 'html',
                    'title': 'text',
                    'url': 'text', 
                    'body_text': 'body_text',
                    'important_text': 'body_text',
                    'forms_html': 'html'
                }
                
                for key, content in raw_data.items():
                    if isinstance(content, str) and key in content_type_map:
                        content_type = content_type_map[key]
                        raw_data[key] = self._filter_noise_from_text(content, content_type)
            
            return raw_data
            
        except Exception as e:
            self.logger.error(f"Error extracting raw content: {e}")
            return {'error': str(e)}

    def _get_body_text(self, driver: webdriver.Remote) -> str:
        """Get clean text from body element."""
        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            return body.text or ""
        except:
            return ""

    def _extract_important_text(self, driver: webdriver.Remote) -> str:
        """Extract text from important page elements."""
        return ""


    def _extract_forms_html(self, driver: webdriver.Remote) -> str:
        """Extract HTML of all forms."""
        return ""

    def _filter_noise_from_text(self, text: str, content_type: str = 'text') -> str:
        """Remove noise patterns with smart whitespace handling."""
        try:
            filtered = text
            
            # Apply noise patterns first
            for pattern in self.noise_patterns:
                filtered = re.sub(pattern, '', filtered, flags=re.IGNORECASE)
            
            # Smart whitespace normalization based on content type
            if content_type == 'html':
                # For HTML: Preserve line breaks but clean up excessive whitespace
                filtered = re.sub(r'[ \t]+', ' ', filtered)  # Multiple spaces/tabs → single space
                filtered = re.sub(r'\n\s*\n\s*\n+', '\n\n', filtered)  # Multiple newlines → double newline
                filtered = filtered.strip()
                
            elif content_type == 'body_text':
                # For body text: Keep line breaks for readability
                lines = filtered.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = re.sub(r'\s+', ' ', line).strip()  # Clean each line
                    if line:  # Keep non-empty lines
                        cleaned_lines.append(line)
                filtered = '\n'.join(cleaned_lines)
                
            else:
                # For titles, URLs: Single line normalization
                filtered = re.sub(r'\s+', ' ', filtered).strip()
            
            return filtered
            
        except Exception as e:
            self.logger.warning(f"Error filtering text: {e}")
            return text

    # ===== STRUCTURED CONTENT EXTRACTION =====

    def _extract_structured_content(self, driver: webdriver.Remote) -> Dict[str, Any]:
        """Extract structured content (forms, buttons, patterns, etc.)."""
        try:
            return {
                'forms': self._extract_forms_info(driver),
                'buttons': self._extract_buttons_info(driver),
                'links': self._extract_links_info(driver),
            }
        except Exception as e:
            self.logger.error(f"Error extracting structured content: {e}")
            return {'error': str(e)}
    
    def _extract_forms_info(self, driver: webdriver.Remote) -> List[Dict[str, Any]]:
        """Extract detailed form information."""
        try:
            forms = driver.find_elements(By.TAG_NAME, 'form')
            forms_info = []
            
            for i, form in enumerate(forms):
                try:
                    forms_info.append({
                        'index': i,
                        'action': form.get_attribute('action') or "",
                        'method': form.get_attribute('method') or "GET",
                        'id': form.get_attribute('id') or "",
                        'class': form.get_attribute('class') or "",
                        'inputs_count': len(form.find_elements(By.TAG_NAME, 'input')),
                        'buttons_count': len(form.find_elements(By.TAG_NAME, 'button')),
                        'is_visible': form.is_displayed(),
                        'text_content': form.text.strip()
                    })
                except:
                    forms_info.append({'index': i, 'error': 'extraction_failed'})
            
            return forms_info
        except:
            return []

    def _extract_buttons_info(self, driver: webdriver.Remote) -> List[Dict[str, Any]]:
        """Extract button and submit element information."""
        try:
            # Get buttons and submit inputs
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            submits = driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
            all_interactive = buttons + submits
            
            buttons_info = []
            
            for i, element in enumerate(all_interactive[:10]):  # Max 10 elements
                try:
                    buttons_info.append({
                        'index': i,
                        'tag': element.tag_name,
                        'type': element.get_attribute('type') or "",
                        'text': (element.text.strip() or element.get_attribute('value') or "")[:100],
                        'id': element.get_attribute('id') or "",
                        'class': element.get_attribute('class') or "",
                        'is_visible': element.is_displayed(),
                        'is_enabled': element.is_enabled()
                    })
                except:
                    buttons_info.append({'index': i, 'error': 'extraction_failed'})
            
            return buttons_info
        except:
            return []
    
    def _extract_links_info(self, driver: webdriver.Remote) -> Dict[str, Any]:
        """Extract detailed link information with full metadata."""
        try:
            links = driver.find_elements(By.TAG_NAME, 'a')
            
            links_info = {
                'total_count': len(links),
                'with_href': 0,
                'external_links': 0,
                'registration_links': [],
                'all_links': []  # Store ALL links with metadata
            }
            
            current_domain = driver.current_url
            
            for i, link in enumerate(links):
                try:
                    href = link.get_attribute('href') or ""
                    text = link.text.strip()
                    title = link.get_attribute('title') or ""
                    target = link.get_attribute('target') or ""
                    
                    # Store complete link data
                    link_data = {
                        'index': i,
                        'href': href,
                        'text': text,
                        'title': title,
                        'target': target,
                        'is_external': False,
                        'is_registration': False,
                        'is_visible': link.is_displayed()
                    }
                    
                    if href:
                        links_info['with_href'] += 1
                        
                        # Check if external
                        if href.startswith('http') and current_domain not in href:
                            links_info['external_links'] += 1
                            link_data['is_external'] = True
                        
                        # Check for registration-related links
                        reg_keywords = ['anmeld', 'register', 'registration', 'buchung', 'enrollment', 'signup', 'einschreibung']
                        text_lower = text.lower()
                        href_lower = href.lower()
                        
                        if any(keyword in text_lower or keyword in href_lower for keyword in reg_keywords):
                            links_info['registration_links'].append({
                                'index': i,
                                'text': text,
                                'href': href,
                                'title': title
                            })
                            link_data['is_registration'] = True
                    
                    # Add to all links
                    links_info['all_links'].append(link_data)
                    
                except Exception as e:
                    links_info['all_links'].append({
                        'index': i,
                        'error': f'extraction_failed: {str(e)}'
                    })
                    continue
            
            return links_info
            
        except Exception as e:
            return {'error': f'links_extraction_failed: {str(e)}'}
    