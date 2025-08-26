
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from automation.linkedin_content_automation import LinkedInContentAutomation

from dotenv import load_dotenv
load_dotenv()


class LinkedInPostContentAutomation:
    def __init__(self):
        """Initialize LinkedIn post content automation"""
        self.driver = None
        self.wait = None
        self.isLogin = False
        self.cookies_file = "linkedin_cookies.json"
        self.session_initialized = False
        
        # Load environment variables
        load_dotenv()
        
        # Use correct environment variable names from template
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        
        # Check if credentials are available
        if not self.email or not self.password:
            raise ValueError(
                "LinkedIn credentials not found! Please create a .env file with:\n"
                "LINKEDIN_EMAIL=your_email@example.com\n"
                "LINKEDIN_PASSWORD=your_password"
            )
        
        print(f"LinkedIn credentials loaded for: {self.email}")
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimized options"""
        try:
            # Quit existing driver if any
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            # Remove --disable-javascript as LinkedIn needs JS
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Memory management and crash prevention
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            chrome_options.add_argument("--js-flags=--max-old-space-size=4096")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-crash-reporter")
            chrome_options.add_argument("--no-crash-upload")
            
            # User agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up driver: {e}")
            self.driver = None
            print(f"Error setting up driver: {e}")
            return False

    def login_to_linkedin(self):
        """Login to LinkedIn with credentials from config"""
        try:
            print("🔐 Starting LinkedIn login process...")
            
            # Navigate to LinkedIn login page
            print("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for page to fully load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            
            print("Looking for email field...")
            # Updated selectors for current LinkedIn login page
            email_selectors = [
                "#username", 
                "input[name='session_key']", 
                "input[type='email']",
                "input[autocomplete='username']",
                "input[data-test-id='username']"
            ]
            email_field = None
            
            for selector in email_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found email field with selector: {selector}")
                    break
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if not email_field:
                # Take screenshot for debugging
                screenshot_path = "login_page_debug.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"❌ Could not find email field. Screenshot saved: {screenshot_path}")
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                return False
                
            email_field.clear()
            time.sleep(1)
            email_field.send_keys(self.email)
            print(f"✅ Entered email: {self.email}")
            
            print("Looking for password field...")
            password_selectors = [
                "#password", 
                "input[name='session_password']", 
                "input[type='password']",
                "input[autocomplete='current-password']",
                "input[data-test-id='password']"
            ]
            password_field = None
            
            for selector in password_selectors:
                try:
                    print(f"Trying password selector: {selector}")
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found password field with selector: {selector}")
                    break
                except Exception as e:
                    print(f"Password selector {selector} failed: {e}")
                    continue
            
            if not password_field:
                print("❌ Could not find password field")
                return False
                
            password_field.clear()
            time.sleep(1)
            password_field.send_keys(self.password)
            print("✅ Entered password")
            
            # Click login button with multiple selectors
            print("Looking for login button...")
            login_selectors = [
                "button[type='submit']",
                "button[data-id='sign-in-form__submit-btn']",
                ".btn__primary--large",
                "input[type='submit']"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_enabled():
                        break
                except:
                    continue
            
            if not login_button:
                print("❌ Could not find login button")
                return False
            
            print(f"Login button found: {login_button.text}")
            
            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(1)
            login_button.click()
            print("✅ Clicked login button")
            
            # Wait for login to process with longer timeout
            print("⏳ Waiting for login to complete...")
            time.sleep(5)
            
            # Check for successful login with more comprehensive indicators
            success_indicators = [
                ".global-nav",
                ".feed-identity-module", 
                "[data-control-name='identity_welcome_message']",
                ".profile-rail-card",
                ".share-box-feed-entry__trigger",
                ".artdeco-button--primary"
            ]
            
            login_successful = False
            for indicator in success_indicators:
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                    )
                    print(f"✅ Login successful! Found indicator: {indicator}")
                    login_successful = True
                    break
                except:
                    continue
            
            # Additional check - verify we're not on login page anymore
            current_url = self.driver.current_url
            if not login_successful and "linkedin.com" in current_url and "login" not in current_url:
                print("✅ Login successful - redirected to feed")
                login_successful = True
            
            if not login_successful:
                # Check for error messages
                error_selectors = [
                    ".alert-error",
                    ".error-message", 
                    "[data-test-id='login-error']",
                    ".form__label--error"
                ]
                
                for selector in error_selectors:
                    try:
                        error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if error_element.is_displayed():
                            print(f"❌ Login error: {error_element.text}")
                            return False
                    except:
                        continue
                
                # Check if still on login page
                if "login" in current_url.lower():
                    print(f"❌ Still on login page: {current_url}")
                    return False
                
                print("⚠️ Login status unclear, assuming failed")
                return False
            
            self.isLogin = True
            print("🎉 Successfully logged in to LinkedIn!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed with exception: {e}")
            # Take screenshot for debugging
            try:
                screenshot_path = "login_error_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot saved to: {screenshot_path}")
            except:
                pass
            return False

    def extract_post_text_from_html(post_html):
        """Extract text from LinkedIn post HTML content."""
        soup = BeautifulSoup(post_html, "html.parser")
        # Remove any script or style tags
        for tag in soup(["script", "style"]):
            tag.decompose()
        # Replace <br> with newlines
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for span in soup.find_all("span"):
            span.unwrap()
        return soup.get_text(separator=" ", strip=True)

    def ensure_session(self):
        """Ensure we have a valid LinkedIn session without repeated logins"""
        if self.session_initialized and self.driver and self.isLogin:
            # Check if session is still valid
            try:
                current_url = self.driver.current_url
                if "linkedin.com" in current_url and "login" not in current_url:
                    print("✅ Existing session is still valid")
                    return True
            except:
                pass
        
        # Initialize or refresh session
        if not self.setup_driver():
            raise Exception("Failed to setup Chrome driver")
        
        if not self.driver:
            raise Exception("Driver is None after setup")
        
        print(f"🌐 Navigating to LinkedIn...")
        self.driver.get("https://www.linkedin.com/feed/")
        
        # Try loading existing cookies first
        if self.load_cookies():
            self.driver.refresh()
            time.sleep(3)
            current_url = self.driver.current_url
            
            # Check if cookies worked
            if "login" not in current_url and "authwall" not in current_url:
                print("✅ Reused existing LinkedIn session")
                self.isLogin = True
                self.session_initialized = True
                self.dismiss_popups()
                return True
            else:
                print("⚠️ Cookies expired, need fresh login")
                # Clear expired cookies
                if os.path.exists(self.cookies_file):
                    os.remove(self.cookies_file)
        
        # Need fresh login
        print("🔑 Performing fresh login...")
        if not self.login_to_linkedin():
            raise Exception("Login failed")
        
        # Save cookies and mark session as initialized
        self.save_cookies()
        self.isLogin = True
        self.session_initialized = True
        
        # Navigate back to feed and dismiss popups
        self.driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)
        self.dismiss_popups()
        
        print("✅ Fresh login completed")
        return True
    
    def find_content(self, url):
        """Scrape the content of a LinkedIn post from a given URL."""
        try:
            # Ensure we have a valid session
            self.ensure_session()
            
            # Handle different LinkedIn URLs
            if url and url != "https://www.linkedin.com/feed/":
                print(f"🔗 Navigating to specific URL: {url}")
                self.driver.get(url)
                time.sleep(3)
                
                # Check if we got redirected to login (session expired)
                current_url = self.driver.current_url
                if "login" in current_url or "authwall" in current_url:
                    print("⚠️ Session expired, refreshing...")
                    self.session_initialized = False
                    self.ensure_session()
                    self.driver.get(url)
                    time.sleep(3)
            
            # Try to find and extract post content with multiple selectors
            post_selectors = [
                # Updated LinkedIn selectors (2024)
                ".feed-shared-update-v2__description-wrapper .break-words",
                ".feed-shared-text .break-words",
                ".feed-shared-update-v2__description .break-words",
                "[data-test-id='post-text']",
                ".update-components-text",
                ".feed-shared-text__text-view",
                ".feed-shared-update-v2__description",
                ".feed-shared-text",
                # Fallback selectors
                "[data-test-id='main-feed-activity-card'] .break-words",
                ".update-components-text .break-words",
                ".share-update-card__update-text",
                ".attributed-text-segment-list__content"
            ]
            
            post_content = None
            for selector in post_selectors:
                try:
                    post_container = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if post_container and post_container.text.strip():
                        post_content = {
                            "text": post_container.text.strip(),
                            "html": post_container.get_attribute("innerHTML")
                        }
                        print(f"✅ Found post content using selector: {selector}")
                        break
                except:
                    continue
            
            if post_content:
                return post_content
            else:
                print("⚠️ No post content found with any selector")
                # Debug: Save screenshot and page source for troubleshooting
                try:
                    self.driver.save_screenshot("debug_post_scraping.png")
                    print(f"📸 Debug screenshot saved: debug_post_scraping.png")
                    print(f"🔗 Current URL: {self.driver.current_url}")
                    print(f"📄 Page title: {self.driver.title}")
                except:
                    pass
                return {"text": "No content found", "html": "", "error": "Could not locate post content with any selector"}
        except Exception as e:
            print(f"❌ Error scraping post content: {e}")
            return {"error": f"Failed to scrape post: {str(e)}"}

    def save_cookies(self):
        """Save LinkedIn cookies to file"""
        try:
            with open(self.cookies_file, "w") as f:
                json.dump(self.driver.get_cookies(), f)
            print("✅ Cookies saved")
        except Exception as e:
            print(f"⚠️ Error saving cookies: {e}")
    
    def load_cookies(self):
        """Load cookies from file to maintain session"""
        try:
            if not os.path.exists(self.cookies_file):
                return False
            
            if os.path.getsize(self.cookies_file) == 0:
                os.remove(self.cookies_file)
                return False
            
            with open(self.cookies_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    os.remove(self.cookies_file)
                    return False
                cookies = json.loads(content)
                
            if not cookies or not isinstance(cookies, list):
                os.remove(self.cookies_file)
                return False
                
            for cookie in cookies:
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    continue
                    
            print("✅ Cookies loaded")
            return True
            
        except Exception as e:
            print(f"⚠️ Error loading cookies: {e}")
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
            return False
    
    def dismiss_popups(self):
        """Dismiss various LinkedIn popups and modals"""
        popup_selectors = [
            (By.XPATH, "//button[contains(@aria-label, 'Dismiss')]"),
            (By.XPATH, "//button[contains(text(), 'Not now')]"),
            (By.XPATH, "//button[contains(text(), 'Maybe later')]"),
            (By.XPATH, "//button[contains(text(), 'Skip')]"),
            (By.XPATH, "//button[contains(text(), 'No thanks')]"),
            (By.XPATH, "//button[@aria-label='Close']"),
            (By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]"),
        ]
        
        dismissed_count = 0
        for selector_type, selector in popup_selectors:
            try:
                popup_elements = self.driver.find_elements(selector_type, selector)
                for element in popup_elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        dismissed_count += 1
                        time.sleep(1)
            except Exception:
                continue
        
        if dismissed_count > 0:
            print(f"📝 Dismissed {dismissed_count} popups")
            time.sleep(2)
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.session_initialized = False
            print("WebDriver closed.")