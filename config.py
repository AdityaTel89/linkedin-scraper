"""
Production-ready configuration for LinkedIn Scraper
Uses environment variables for sensitive data
Optimized for Railway deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# ==================== ENVIRONMENT DETECTION ====================
# Detect Railway production environment
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None
IS_PRODUCTION = IS_RAILWAY or os.getenv('FLASK_ENV', 'development') == 'production'

# ==================== AUTHENTICATION ====================
# LinkedIn credentials - NEVER hardcode in production!
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

# Validate credentials are set
if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    print("⚠️  WARNING: LinkedIn credentials not set in environment variables")
    print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in Railway dashboard")

# ==================== FILE PATHS ====================
# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Profile URLs file
PROFILE_URLS_FILE = os.path.join(BASE_DIR, os.getenv('PROFILE_URLS_FILE', 'profile_urls.txt'))

# Output CSV file name (with timestamp support)
OUTPUT_CSV = os.path.join(BASE_DIR, os.getenv('OUTPUT_CSV', 'linkedin_profiles.csv'))

# Logs directory
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Debug files directory
DEBUG_DIR = os.path.join(BASE_DIR, 'debug')
os.makedirs(DEBUG_DIR, exist_ok=True)

# ==================== SCRAPING CONFIGURATION ====================
# Timing configurations (in seconds)
MIN_DELAY = int(os.getenv('MIN_DELAY', '30'))  # Minimum delay between profile scrapes
MAX_DELAY = int(os.getenv('MAX_DELAY', '90'))  # Maximum delay between profile scrapes
LONG_BREAK = int(os.getenv('LONG_BREAK', '180'))  # Long break after every N profiles
LONG_BREAK_INTERVAL = int(os.getenv('LONG_BREAK_INTERVAL', '5'))  # Profiles before long break

# Retry configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))  # Maximum retry attempts for failed profiles
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '60'))  # Delay before retry (seconds)

# ==================== BROWSER CONFIGURATION ====================
# Chrome options - Auto-enable headless mode on Railway
HEADLESS_MODE = IS_PRODUCTION or os.getenv('HEADLESS_MODE', 'False').lower() == 'true'

# Browser window size
WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1920'))
WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '1080'))

# Page load timeout (seconds)
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

# Element wait timeout (seconds)
ELEMENT_WAIT_TIMEOUT = int(os.getenv('ELEMENT_WAIT_TIMEOUT', '20'))

# ==================== USER AGENTS ====================
# User agents for rotation (latest browsers - Linux for production)
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

# ==================== PROXY CONFIGURATION ====================
# Proxy settings (optional - for production use)
USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
PROXY_HOST = os.getenv('PROXY_HOST', '')
PROXY_PORT = os.getenv('PROXY_PORT', '')
PROXY_USERNAME = os.getenv('PROXY_USERNAME', '')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', '')

# Construct proxy URL if configured
if USE_PROXY and PROXY_HOST and PROXY_PORT:
    if PROXY_USERNAME and PROXY_PASSWORD:
        PROXY_URL = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    else:
        PROXY_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"
else:
    PROXY_URL = None

# ==================== LOGGING CONFIGURATION ====================
# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
LOG_FILE = os.path.join(LOGS_DIR, os.getenv('LOG_FILE', 'scraper.log'))

# Maximum log file size (bytes)
MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', str(10 * 1024 * 1024)))  # 10 MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))  # Number of backup log files

# ==================== RATE LIMITING ====================
# Maximum profiles per session
MAX_PROFILES_PER_SESSION = int(os.getenv('MAX_PROFILES_PER_SESSION', '100'))

# Maximum concurrent scraping sessions
MAX_CONCURRENT_SESSIONS = int(os.getenv('MAX_CONCURRENT_SESSIONS', '1'))

# ==================== DATA EXTRACTION ====================
# Maximum text length for fields
MAX_ABOUT_LENGTH = int(os.getenv('MAX_ABOUT_LENGTH', '1000'))
MAX_HEADLINE_LENGTH = int(os.getenv('MAX_HEADLINE_LENGTH', '300'))
MAX_POSITION_LENGTH = int(os.getenv('MAX_POSITION_LENGTH', '500'))

# ==================== FEATURE FLAGS ====================
# Enable/disable features - Disable debug in production for performance
SAVE_DEBUG_HTML = (not IS_PRODUCTION) and os.getenv('SAVE_DEBUG_HTML', 'True').lower() == 'true'
SAVE_DEBUG_SCREENSHOTS = (not IS_PRODUCTION) and os.getenv('SAVE_DEBUG_SCREENSHOTS', 'True').lower() == 'true'
ENABLE_CAPTCHA_DETECTION = os.getenv('ENABLE_CAPTCHA_DETECTION', 'True').lower() == 'true'

# ==================== SECURITY ====================
# Security settings
ALLOWED_DOMAINS = ['linkedin.com', 'www.linkedin.com']  # Only allow LinkedIn URLs

# ==================== FLASK APP CONFIGURATION ====================
# Flask settings (for web UI)
FLASK_ENV = 'production' if IS_PRODUCTION else os.getenv('FLASK_ENV', 'development')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())

# Railway provides PORT environment variable automatically
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('PORT', os.getenv('FLASK_PORT', '8080')))  # Railway uses PORT
FLASK_DEBUG = (not IS_PRODUCTION) and os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# ==================== CONFIGURATION VALIDATION ====================
def validate_config():
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    # Check required settings
    if not LINKEDIN_EMAIL:
        errors.append("LINKEDIN_EMAIL is not set")
    
    if not LINKEDIN_PASSWORD:
        errors.append("LINKEDIN_PASSWORD is not set")
    
    # Check timing configurations
    if MIN_DELAY > MAX_DELAY:
        errors.append("MIN_DELAY cannot be greater than MAX_DELAY")
    
    if MIN_DELAY < 5:
        warnings.append("MIN_DELAY is very low (<5s) - may trigger rate limiting")
    
    # Check proxy configuration
    if USE_PROXY and not PROXY_URL:
        errors.append("USE_PROXY is enabled but proxy details are incomplete")
    
    # Railway-specific warnings
    if IS_RAILWAY and not HEADLESS_MODE:
        warnings.append("Running on Railway but HEADLESS_MODE is disabled - this may cause issues")
    
    # Display results
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    return True

# ==================== CONFIGURATION DISPLAY ====================
def display_config():
    """Display current configuration (for debugging)"""
    print("\n" + "="*60)
    print("LinkedIn Scraper Configuration")
    print("="*60)
    print(f"Environment: {FLASK_ENV}")
    print(f"Platform: {'Railway' if IS_RAILWAY else 'Local/Other'}")
    print(f"Production Mode: {IS_PRODUCTION}")
    print(f"Headless Mode: {HEADLESS_MODE}")
    print(f"Min Delay: {MIN_DELAY}s")
    print(f"Max Delay: {MAX_DELAY}s")
    print(f"Long Break: {LONG_BREAK}s (every {LONG_BREAK_INTERVAL} profiles)")
    print(f"Max Profiles/Session: {MAX_PROFILES_PER_SESSION}")
    print(f"Proxy Enabled: {USE_PROXY}")
    print(f"Debug HTML: {SAVE_DEBUG_HTML}")
    print(f"Debug Screenshots: {SAVE_DEBUG_SCREENSHOTS}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Flask Port: {FLASK_PORT}")
    print("="*60 + "\n")

# Auto-validate on import (only show warnings in production)
if not IS_PRODUCTION:
    if not validate_config():
        print("\n⚠️  Please fix configuration errors before running the scraper\n")
else:
    # In production, just validate silently
    validate_config()
