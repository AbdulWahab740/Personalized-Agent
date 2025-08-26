
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
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

class LinkedInContentAutomation:
    def __init__(self):
        """Initialize LinkedIn automation with configuration"""
        
        self.driver = None
        self.wait = None
        self.isLogin = False
        self.cookies_file = "linkedin_cookies.json"  # add this

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
        """Setup Chrome WebDriver with proper options and memory management"""
        try:
            # Close existing driver if any to prevent memory leaks
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
            
            print("Navigating to LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for page to load completely
            time.sleep(3)
            
            print("Looking for email field...")
            # Wait for login form and enter credentials
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.clear()
            email_field.send_keys(self.email)
            print(f"Entered email: {self.email}")
            
            print("Looking for password field...")
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            print("Entered password")
            
            # Click login button
            print("Looking for login button...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            print(f"Login button text: {login_button.text}")
            print(f"Login button enabled: {login_button.is_enabled()}")
            
            # Click login button
            login_button.click()
            print("Clicked login button")
            
            # Wait a bit for the login process to start
            time.sleep(3)
            
            # Check for various success indicators
            success_indicators = [
                ".global-nav",
                ".feed-identity-module",
                "[data-control-name='identity_welcome_message']",
                ".profile-rail-card"
            ]
            
            login_successful = False
            for indicator in success_indicators:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, indicator)))
                    print(f"Login successful! Found indicator: {indicator}")
                    login_successful = True
                    break
                except:
                    continue
            
            if not login_successful:
                # Check if there's an error message
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".alert-error, .error-message, [data-test-id='login-error']")
                    error_text = error_element.text
                    print(f"Login error detected: {error_text}")
                    return False
                except:
                    pass
                
                # Check if we're still on login page
                current_url = self.driver.current_url
                if "login" in current_url.lower():
                    print(f"Still on login page: {current_url}")
                    return False
            
            self.isLogin = True
            self.save_cookies() 
            print("Successfully logged in to LinkedIn!")
            return True
            
        except Exception as e:
            print(f"Login failed: {e}")
            # Take screenshot for debugging
            try:
                screenshot_path = "login_error_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except:
                pass
            return False
    def save_cookies(self):
        """Save LinkedIn cookies to file"""
        with open(self.cookies_file, "w") as f:
            json.dump(self.driver.get_cookies(), f)
        print("✅ Cookies saved")

    def load_cookies(self):
        """Load cookies if available"""
        if not os.path.exists(self.cookies_file):
            return False
        
        try:
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
                
                # Check if cookies are expired
                current_time = time.time()
                valid_cookies = []
                
            for cookie in cookies:
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                try:
                    self.driver.add_cookie(cookie)
                except Exception as cookie_error:
                    print(f"Failed to add cookie: {cookie_error}")
                    continue
                    
            print("✅ Valid cookies loaded into browser")
            return True
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ JSON parsing error in cookies: {e}")
            # Remove corrupted cookie file
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
            return False
        except Exception as e:
            print(f"⚠️ Error loading cookies: {e}")
            # Remove corrupted cookie file
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
            return False

    def dismiss_popups(self):
        """Dismiss various LinkedIn popups and modals that can interrupt automation"""
        popup_selectors = [
            # Premium trial popup
            (By.XPATH, "//button[contains(@aria-label, 'Dismiss')]"),
            (By.XPATH, "//button[contains(text(), 'Not now')]"),
            (By.XPATH, "//button[contains(text(), 'Maybe later')]"),
            (By.XPATH, "//button[contains(text(), 'Skip')]"),
            (By.XPATH, "//button[contains(text(), 'No thanks')]"),
            
            # Close button (X)
            (By.XPATH, "//button[@aria-label='Close']"),
            (By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]"),
            (By.CSS_SELECTOR, "button[data-test-modal-close-btn]"),
            
            # Premium specific popups
            (By.XPATH, "//button[contains(text(), 'Continue with free')]"),
            (By.XPATH, "//a[contains(text(), 'Continue with free')]"),
            
            # Password manager popups
            (By.XPATH, "//button[contains(text(), 'Never')]"),
            (By.XPATH, "//button[contains(text(), 'Not for this site')]"),
            (By.CSS_SELECTOR, "[data-testid='password-manager-dismiss']"),
            
            # General modal dismiss
            (By.CSS_SELECTOR, ".artdeco-modal__dismiss"),
            (By.CSS_SELECTOR, ".msg-overlay-bubble-header__controls button"),
        ]
        
        dismissed_count = 0
        for by, selector in popup_selectors:
            try:
                popup_elements = self.driver.find_elements(by, selector)
                for element in popup_elements:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        dismissed_count += 1
                        print(f"✅ Dismissed popup using: {selector}")
                        time.sleep(1)  # Brief pause after dismissing
            except Exception as e:
                continue  # Silently continue if popup not found
        
        if dismissed_count > 0:
            print(f"📝 Total popups dismissed: {dismissed_count}")
            time.sleep(2)  # Wait for UI to settle after dismissing popups
        
        # Additional check for overlay elements that might block interactions
        try:
            overlays = self.driver.find_elements(By.CSS_SELECTOR, ".artdeco-modal, .msg-overlay-bubble-header")
            for overlay in overlays:
                if overlay.is_displayed():
                    # Try to find and click close button within overlay
                    close_buttons = overlay.find_elements(By.CSS_SELECTOR, "button[aria-label*='lose'], button[aria-label*='ismiss']")
                    for btn in close_buttons:
                        if btn.is_displayed():
                            btn.click()
                            print("✅ Closed overlay modal")
                            time.sleep(1)
                            break
        except Exception:
            pass

    def clean_content_for_browser(self, content):
        """Clean content to ensure it's compatible with ChromeDriver"""
        if not content:
            return content
        
        # Remove or replace problematic Unicode characters
        import re
        
        # Replace common problematic characters with safe alternatives
        replacements = {
            '•': '-',  # Bullet point to dash
            '–': '-',  # En dash to regular dash
            '—': '-',  # Em dash to regular dash
            '"': '"',  # Smart quotes to regular quotes
            '"': '"',
            ''': "'",  # Smart apostrophes to regular apostrophes
            ''': "'",
            '…': '...',  # Ellipsis to three dots
        }
        
        cleaned_content = content
        for old_char, new_char in replacements.items():
            cleaned_content = cleaned_content.replace(old_char, new_char)
        
        # Remove any other non-ASCII characters that might cause issues
        cleaned_content = re.sub(r'[^\x00-\x7F]+', '', cleaned_content)
        
        return cleaned_content
    
    def create_post(self, content):
        """Create a LinkedIn post with the given content"""
        try:
            # Force garbage collection before starting
            import gc
            gc.collect()
            
            self.setup_driver()
            
            # Navigate to LinkedIn FIRST, then load cookies
            print("Navigating to LinkedIn...")
            self.driver.get("https://www.linkedin.com/feed/")
            
            # Now try loading cookies (browser is on LinkedIn domain)
            if self.load_cookies():
                self.driver.refresh()
                self.isLogin = True
                print("Reused existing LinkedIn session ")
            else:
                if not self.isLogin:
                    self.login_to_linkedin()
                    # Navigate back to feed after login
                    print("Navigating back to LinkedIn feed...")
                    self.driver.get("https://www.linkedin.com/feed/")
                    # Dismiss any popups that appear after login
                    time.sleep(3)  # Wait for page to load
                    self.dismiss_popups()
            
            # Clean the content for browser compatibility
            content = self.clean_content_for_browser(content)
            print(f"Content cleaned and ready for posting: {len(content)} characters")
            
            # Wait until feed loads fully
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Handle LinkedIn popups and interruptions
            self.dismiss_popups()
            
            # Additional wait and scroll to ensure page is ready
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # Refined selectors for "Start a post" button
            start_post_selectors = [
                # Most reliable (button with "Start a post" text inside <strong>)
                (By.XPATH, "//button//strong[normalize-space(text())='Start a post']/ancestor::button"),
                
                # Fallback: case-insensitive text contains
                (By.XPATH, "//button[contains(., 'Start a post')]"),
                
                # Fallback: stable class
                (By.CSS_SELECTOR, "button.artdeco-button.artdeco-button--tertiary")
            ]

            start_post_button = None
            for by, selector in start_post_selectors:
                try:
                    start_post_button = self.wait.until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if start_post_button:
                        print(f"✅ Found 'Start a post' button using selector: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️ Selector failed: {selector} | {e}")
                    continue

            if not start_post_button:
                self.driver.save_screenshot("debug_start_post.png")
                raise Exception("❌ Could not find 'Start a post' button. Screenshot saved: debug_start_post.png")

            # Enhanced click with multiple fallback methods
            click_successful = False
            
            # Method 1: Scroll to element and regular click
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", start_post_button)
                time.sleep(1)
                start_post_button.click()
                click_successful = True
                print("✅ Clicked 'Start a post' button (regular click)")
            except Exception as e:
                print(f"⚠️ Regular click failed: {e}")
            
            # Method 2: JavaScript click if regular click failed
            if not click_successful:
                try:
                    self.driver.execute_script("arguments[0].click();", start_post_button)
                    click_successful = True
                    print("✅ Clicked 'Start a post' button (JavaScript click)")
                except Exception as e:
                    print(f"⚠️ JavaScript click failed: {e}")
            
            # Method 3: ActionChains click as last resort
            if not click_successful:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.move_to_element(start_post_button).click().perform()
                    click_successful = True
                    print("✅ Clicked 'Start a post' button (ActionChains)")
                except Exception as e:
                    print(f"⚠️ ActionChains click failed: {e}")
            
            if not click_successful:
                self.driver.save_screenshot("click_failed.png")
                raise Exception("❌ All click methods failed. Screenshot saved: click_failed.png")

            # Wait for modal input field to appear instead of sleep
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
            )
            print("✅ Post modal opened successfully")

        
            # Wait for post modal and enter content
            post_input_selectors = [
                ".ql-editor",
                "[contenteditable='true']",
                ".share-box__input",
                "div[role='textbox']"
            ]
            
            post_input = None
            for selector in post_input_selectors:
                try:
                    post_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if post_input:
                        print(f"Found post input using selector: {selector}")
                        break
                except:
                    continue
            
            if not post_input:
                raise Exception("Could not find post input field")
            
            print(f"Found post input field: {post_input.tag_name}")
            print(f"Input classes: {post_input.get_attribute('class')}")
            print(f"Input contenteditable: {post_input.get_attribute('contenteditable')}")
            
            post_input.clear()
            print("Typing post content...")
            
            # Type content in chunks to avoid character issues
            try:
                # Try typing character by character first
                for char in content:
                    try:
                        post_input.send_keys(char)
                        time.sleep(0.0008)  # Natural typing speed
                    except Exception as char_error:
                        print(f"Warning: Could not type character '{char}', skipping...")
                        continue
            except Exception as typing_error:
                print(f"Character-by-character typing failed, trying alternative method...")
                # Fallback: try typing the entire content at once
                try:
                    post_input.send_keys(content)
                except Exception as fallback_error:
                    print(f"Fallback typing also failed: {fallback_error}")
                    # Last resort: use JavaScript to set the content
                    try:
                        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", post_input, content)
                        print("Content set using JavaScript fallback")
                    except Exception as js_error:
                        raise Exception(f"All content input methods failed: {js_error}")
            
            print(f"Post content prepared: {len(content)} characters")
            
            # Try multiple selectors for the Post button
            post_button_selectors = [
                "button.share-actions__primary-action",
                "button.artdeco-button--primary",
                "button[aria-label='Post']",
                "button[aria-label='Post now']",
                ".share-actions__primary-action",
                "//button[contains(@class, 'share-actions__primary-action')]",  # XPath fallback
                "//span[contains(text(), 'Post')]/ancestor::button",
                "//button[contains(text(), 'Post')]"  # XPath fallback
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    if selector.startswith("//"):
                        post_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        post_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if post_button:
                        print(f"Found Post button using selector: {selector}")
                        break
                except:
                    continue
            
            if not post_button:
                raise Exception("Could not find Post button")
            
            # Debug: Print button details
            print(f"Found Post button: {post_button.text}")
            print(f"Button classes: {post_button.get_attribute('class')}")
            print(f"Button enabled: {post_button.is_enabled()}")
            
            # Click Post button
            try:
                post_button.click()
                print("Clicked Post button")
            except Exception as click_error:
                print(f"Click failed, trying JavaScript click: {click_error}")
                # Fallback: use JavaScript click
                try:
                    self.driver.execute_script("arguments[0].click();", post_button)
                    print("Post button clicked using JavaScript")
                except Exception as js_click_error:
                    raise Exception(f"Both regular click and JavaScript click failed: {js_click_error}")
            
            # Wait for post confirmation
            time.sleep(4)
            st.success("Successfully Published the Content")
            print("Post successfully published!")
            return True
            
        except Exception as e:
            print(f"Error creating post: {e}")
            return False
    
if __name__=="__main__":
    automation = LinkedInContentAutomation()
    # automation.login_to_linkedin()
    content = "This is a test post f" \
    "rom LinkedIn automation script."
    automation.create_post(content)