import time
import random
import csv
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import config


class LinkedInScraper:
    def __init__(self):
        """Initialize the scraper with Chrome driver and stealth settings"""
        print("🚀 Initializing LinkedIn Scraper...")
        
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        
        # Check if we should run headless (from config)
        if config.HEADLESS_MODE:
            print("   🎭 Running in HEADLESS mode (production)")
            # Production headless settings
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--remote-debugging-port=9222')
        else:
            print("   🖥️  Running in VISIBLE mode (local development)")
            chrome_options.add_argument("--start-maximized")
        
        # Common settings
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set random user agent
        user_agent = random.choice(config.USER_AGENTS)
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Initialize driver
        try:
            print("   🔧 Attempting to initialize Chrome...")
            
            if config.IS_RAILWAY:
                # Railway production: use system chromium
                print("   🚂 Railway detected - using system chromium")
                
                # Find chromium and chromedriver paths
                try:
                    chromium_path = subprocess.check_output(['which', 'chromium']).decode().strip()
                    chromedriver_path = subprocess.check_output(['which', 'chromedriver']).decode().strip()
                    print(f"   📍 Chromium: {chromium_path}")
                    print(f"   📍 ChromeDriver: {chromedriver_path}")
                except subprocess.CalledProcessError:
                    # Fallback to common paths
                    chromium_path = '/usr/bin/chromium'
                    chromedriver_path = '/usr/bin/chromedriver'
                    print(f"   📍 Using fallback paths")
                
                chrome_options.binary_location = chromium_path
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            else:
                # Local development: use webdriver-manager
                print("   💻 Local development - using webdriver-manager")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("   ✅ Chrome initialized successfully")
            
        except Exception as e:
            print(f"   ❌ Fatal error: {e}")
            raise Exception(f"Chrome initialization failed: {e}")
        
        # Apply stealth settings
        platform_val = "Linux" if config.HEADLESS_MODE else "Win32"
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform=platform_val,
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        self.wait = WebDriverWait(self.driver, 20)
        self.profiles_scraped = []
        print("✅ Scraper initialized successfully\n")
    
    def login(self):
        """Login to LinkedIn with credentials from config"""
        print("🔐 Logging into LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))
            
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self._human_type(email_field, config.LINKEDIN_EMAIL)
            time.sleep(random.uniform(1, 2))
            
            password_field = self.driver.find_element(By.ID, "password")
            self._human_type(password_field, config.LINKEDIN_PASSWORD)
            time.sleep(random.uniform(1, 2))
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(random.uniform(8, 12))
            
            current_url = self.driver.current_url
            
            if "feed" in current_url or "mynetwork" in current_url:
                print("✅ Login successful!\n")
                return True
            elif "checkpoint" in current_url or "challenge" in current_url:
                print("⚠️  LinkedIn security challenge detected!")
                if not config.HEADLESS_MODE:
                    print("   Please complete verification in the browser window...")
                    input("   Press Enter after completing the challenge...")
                    return True
                else:
                    print("   Cannot handle CAPTCHA in headless mode")
                    return False
            else:
                print("⚠️  Login status unclear")
                print(f"   Current URL: {current_url}")
                if not config.HEADLESS_MODE:
                    input("   Press Enter to continue if you see you're logged in...")
                    return True
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def _human_type(self, element, text):
        """Simulate human typing with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def scrape_profile(self, profile_url):
        """Scrape a single LinkedIn profile"""
        print(f"\n📊 Scraping: {profile_url}")
        
        try:
            self.driver.get(profile_url)
            time.sleep(random.uniform(6, 10))
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"   📍 Loaded URL: {current_url}")
            print(f"   📄 Page Title: {page_title}")
            
            if "authwall" in current_url:
                print("   🚫 BLOCKED: AuthWall detected")
                return self._create_error_profile(profile_url, "AuthWall")
            
            if "feed" in current_url or current_url == "https://www.linkedin.com/":
                print("   ⚠️  WARNING: Redirected to feed instead of profile")
                time.sleep(5)
                self.driver.get(profile_url)
                time.sleep(8)
            
            self._scroll_page()
            time.sleep(random.uniform(3, 5))
            
            profile_data = self._extract_from_page_text(profile_url)
            
            print(f"   ✅ Name: {profile_data.get('name', 'N/A')}")
            print(f"   ✅ Headline: {profile_data.get('headline', 'N/A')[:50]}...")
            
            return profile_data
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return self._create_error_profile(profile_url, str(e))
    
    def _extract_from_page_text(self, url):
        """Extract profile data from page text"""
        profile_data = {'url': url}
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            seen = set()
            unique_lines = []
            for line in lines:
                if line not in seen and len(line) > 0:
                    seen.add(line)
                    unique_lines.append(line)
            
            lines = unique_lines
            
            skip_keywords = [
                'home', 'my network', 'jobs', 'messaging', 'notifications', 'search', 
                'menu', 'for business', 'accessibility', 'linkedin corporation',
                'talent solutions', 'community guidelines', 'marketing solutions',
                'privacy & terms', 'advertising', 'sales solutions', 'small business',
                'safety center', '© 2025', 'try premium'
            ]
            
            filtered_lines = []
            for line in lines:
                line_lower = line.lower()
                if not any(skip in line_lower for skip in skip_keywords):
                    filtered_lines.append(line)
            
            lines = filtered_lines
            
            # Extract Name
            name = "Not found"
            for line in lines[:10]:
                if len(line) > 3 and len(line) < 100:
                    if (' ' in line and not line.startswith('http')) or (8 < len(line) < 50):
                        name = line
                        break
            profile_data['name'] = name
            
            # Extract Headline
            headline = "Not found"
            found_name_idx = -1
            for i, line in enumerate(lines[:20]):
                if name != "Not found" and name in line:
                    found_name_idx = i
                    break
            
            if found_name_idx >= 0:
                for j in range(found_name_idx + 1, min(found_name_idx + 6, len(lines))):
                    potential = lines[j]
                    if len(potential) > 20 and len(potential) < 300:
                        if 'connection' not in potential.lower():
                            headline = potential
                            break
            profile_data['headline'] = headline
            
            # Extract Location
            location = "Not found"
            location_keywords = ['India', 'Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Hyderabad', 
                               'Chennai', 'Maharashtra', 'Karnataka', 'Gujarat', 'Nashik']
            for line in lines[:30]:
                if any(keyword in line for keyword in location_keywords):
                    if len(line) < 100 and 'connection' not in line.lower():
                        location = line
                        break
            profile_data['location'] = location
            
            # Extract About
            about = "Not found"
            about_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == "About":
                    about_idx = i
                    break
            
            if about_idx > 0:
                about_lines = []
                for j in range(about_idx + 1, min(about_idx + 15, len(lines))):
                    line = lines[j].strip()
                    if line in ['Activity', 'Experience', 'Education', 'Skills']:
                        break
                    if len(line) > 10:
                        about_lines.append(line)
                if about_lines:
                    about = ' '.join(about_lines)[:500]
            profile_data['about'] = about
            
            # Extract Current Position
            position = "Not found"
            company_keywords = ['Technologies', 'Company', 'Corporation', 'Institute', 
                              'University', 'Pvt', 'Ltd', 'Solutions', 'Services']
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in company_keywords):
                    if len(line) > 10 and len(line) < 200:
                        position = line
                        break
            profile_data['current_position'] = position
            
            return profile_data
            
        except Exception as e:
            print(f"   ⚠️ Extraction error: {e}")
            return self._create_error_profile(url, str(e))
    
    def _create_error_profile(self, url, error_msg):
        """Create profile data for errors"""
        return {
            'url': url,
            'name': f'ERROR: {error_msg}',
            'headline': 'See error',
            'location': 'See error',
            'about': 'See error',
            'current_position': 'See error'
        }
    
    def _scroll_page(self):
        """Scroll the page to load all dynamic content"""
        try:
            scroll_pause = random.uniform(1, 2)
            for _ in range(4):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                if random.random() > 0.5:
                    self.driver.execute_script("window.scrollBy(0, -400);")
                    time.sleep(scroll_pause / 2)
        except:
            pass
    
    def scrape_all_profiles(self, profile_urls):
        """Scrape all profiles with delays"""
        print(f"\n🎯 Starting to scrape {len(profile_urls)} profiles...\n")
        
        for index, url in enumerate(profile_urls, 1):
            print(f"\n{'='*60}")
            print(f"[{index}/{len(profile_urls)}]", end=" ")
            
            profile_data = self.scrape_profile(url)
            self.profiles_scraped.append(profile_data)
            
            print(f"{'='*60}")
            
            if index < len(profile_urls):
                if index % 5 == 0:
                    print(f"\n⏸️  Taking a long break ({config.LONG_BREAK}s)...\n")
                    time.sleep(config.LONG_BREAK)
                else:
                    delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
                    print(f"\n⏸️  Waiting {delay:.1f}s before next profile...\n")
                    time.sleep(delay)
        
        print(f"\n\n✅ Completed scraping {len(self.profiles_scraped)} profiles!")
    
    def export_to_csv(self):
        """Export scraped data to CSV"""
        print(f"\n💾 Exporting data to {config.OUTPUT_CSV}...")
        
        if not self.profiles_scraped:
            print("⚠️  No data to export!")
            return
        
        all_keys = set()
        for profile in self.profiles_scraped:
            all_keys.update(profile.keys())
        
        column_order = ['name', 'headline', 'location', 'current_position', 'about', 'url']
        ordered_keys = [k for k in column_order if k in all_keys]
        ordered_keys.extend([k for k in sorted(all_keys) if k not in column_order])
        
        with open(config.OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_keys)
            writer.writeheader()
            writer.writerows(self.profiles_scraped)
        
        print(f"✅ Data exported successfully!")
        print(f"   📁 File: {config.OUTPUT_CSV}")
        
        success_count = sum(1 for p in self.profiles_scraped 
                          if 'ERROR' not in str(p.get('name', '')) 
                          and p.get('name') != 'Not found')
        error_count = sum(1 for p in self.profiles_scraped 
                         if 'ERROR' in str(p.get('name', '')))
        not_found_count = len(self.profiles_scraped) - success_count - error_count
        
        print(f"\n📊 Results Summary:")
        print(f"   ✅ Successfully scraped: {success_count}")
        print(f"   ⚠️  Data not found: {not_found_count}")
        print(f"   ❌ Errors: {error_count}")
    
    def close(self):
        """Close the browser"""
        print("\n🔒 Closing browser...")
        try:
            self.driver.quit()
            print("✅ Browser closed. Scraping session ended.")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")
