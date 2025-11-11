from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import threading
import os
import time
import logging
from datetime import datetime
from scraper import LinkedInScraper
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Global state
scraper_instance = None
scraping_lock = threading.Lock()
scraping_status = {
    'is_running': False,
    'progress': [],
    'total': 0,
    'completed': 0,
    'failed': 0,
    'current_profile': '',
    'profiles_data': [],
    'start_time': None,
    'end_time': None
}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraper_instance, scraping_status
    
    with scraping_lock:
        if scraping_status['is_running']:
            return jsonify({'error': 'Scraping is already in progress'}), 400
    
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        urls = data.get('urls', [])
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not urls or len(urls) == 0:
            return jsonify({'error': 'At least one profile URL is required'}), 400
        
        # Validate URLs
        valid_urls = [url for url in urls if url.strip().startswith('http')]
        if len(valid_urls) == 0:
            return jsonify({'error': 'No valid URLs provided'}), 400
        
        # Update config
        config.LINKEDIN_EMAIL = email
        config.LINKEDIN_PASSWORD = password
        
        # Reset status
        scraping_status = {
            'is_running': True,
            'progress': [],
            'total': len(valid_urls),
            'completed': 0,
            'failed': 0,
            'current_profile': '',
            'profiles_data': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        logger.info(f"Starting scraping job for {len(valid_urls)} profiles")
        
        # Start background thread
        thread = threading.Thread(target=scrape_thread, args=(valid_urls,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Scraping started successfully',
            'total': len(valid_urls)
        })
        
    except Exception as e:
        logger.error(f"Error starting scraping: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/stop', methods=['POST'])
def stop_scraping():
    """Stop the scraping process"""
    global scraper_instance, scraping_status
    
    try:
        if scraper_instance:
            scraper_instance.close()
        
        scraping_status['is_running'] = False
        scraping_status['end_time'] = datetime.now().isoformat()
        logger.info("Scraping stopped by user")
        
        return jsonify({'success': True, 'message': 'Scraping stopped'})
    except Exception as e:
        logger.error(f"Error stopping scraping: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_csv():
    """Download the CSV file"""
    try:
        if os.path.exists(config.OUTPUT_CSV):
            return send_file(
                config.OUTPUT_CSV,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'linkedin_profiles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        return jsonify({'error': 'CSV file not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

def scrape_thread(urls):
    """Background scraping thread"""
    global scraper_instance, scraping_status
    
    try:
        scraper_instance = LinkedInScraper()
        
        add_log('🚀 Initializing scraper...')
        
        # Login
        add_log('🔐 Logging into LinkedIn...')
        if not scraper_instance.login():
            add_log('❌ Login failed! Check your credentials.')
            scraping_status['is_running'] = False
            return
        
        add_log('✅ Login successful!')
        add_log(f'📊 Scraping {len(urls)} profiles...')
        
        # Scrape profiles
        for index, url in enumerate(urls, 1):
            if not scraping_status['is_running']:
                add_log('⏹️ Scraping stopped by user')
                break
            
            scraping_status['current_profile'] = url
            add_log(f'\n[{index}/{len(urls)}] Processing: {url}')
            
            try:
                profile_data = scraper_instance.scrape_profile(url)
                scraper_instance.profiles_scraped.append(profile_data)
                
                # Check if successful
                is_success = profile_data.get('name') not in ['Not found', 'ERROR', None]
                
                scraping_status['profiles_data'].append({
                    'index': index,
                    'name': profile_data.get('name', 'Unknown'),
                    'headline': profile_data.get('headline', 'N/A')[:80],
                    'location': profile_data.get('location', 'N/A'),
                    'url': url,
                    'status': 'success' if is_success else 'failed'
                })
                
                if is_success:
                    add_log(f'   ✅ Success: {profile_data.get("name")}')
                    scraping_status['completed'] += 1
                else:
                    add_log(f'   ⚠️ Failed: Could not extract data')
                    scraping_status['failed'] += 1
                
                # Delay between profiles
                if index < len(urls):
                    delay = 30
                    add_log(f'   ⏳ Waiting {delay}s...')
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                add_log(f'   ❌ Error: {str(e)}')
                scraping_status['failed'] += 1
        
        # Export
        add_log('\n💾 Exporting to CSV...')
        scraper_instance.export_to_csv()
        add_log(f'✅ Saved to {config.OUTPUT_CSV}')
        
        add_log(f'\n🎉 Completed! ✅ {scraping_status["completed"]} success, ❌ {scraping_status["failed"]} failed')
        
    except Exception as e:
        logger.error(f"Fatal error in scraping thread: {str(e)}")
        add_log(f'❌ Fatal error: {str(e)}')
    
    finally:
        if scraper_instance:
            try:
                scraper_instance.close()
            except:
                pass
        scraping_status['is_running'] = False
        scraping_status['end_time'] = datetime.now().isoformat()
        logger.info("Scraping completed")

def add_log(message):
    """Add message to progress log"""
    scraping_status['progress'].append({
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    logger.info(message)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("\n" + "=" * 70)
    print("🌐 LinkedIn Scraper - Production Ready".center(70))
    print("=" * 70)
    print(f"📍 Server: http://localhost:{port}")
    print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print("=" * 70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') != 'production',
        threaded=True
    )
