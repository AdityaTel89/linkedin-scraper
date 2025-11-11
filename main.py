import config
from scraper import LinkedInScraper


def load_profile_urls():
    """Load profile URLs from text file"""
    try:
        with open(config.PROFILE_URLS_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        return urls
    except FileNotFoundError:
        print(f"❌ Error: {config.PROFILE_URLS_FILE} not found!")
        print("Please create this file with LinkedIn profile URLs (one per line)")
        return []


def main():
    """Main execution function"""
    print("=" * 60)
    print("          LINKEDIN PROFILE SCRAPER")
    print("=" * 60)
    
    # Load profile URLs
    profile_urls = load_profile_urls()
    
    if not profile_urls:
        return
    
    print(f"\n📋 Loaded {len(profile_urls)} profile URLs")
    
    # Initialize scraper
    scraper = LinkedInScraper()
    
    try:
        # Login to LinkedIn
        if not scraper.login():
            print("❌ Cannot proceed without successful login")
            return
        
        # Scrape all profiles
        scraper.scrape_all_profiles(profile_urls)
        
        # Export to CSV
        scraper.export_to_csv()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        if scraper.profiles_scraped:
            scraper.export_to_csv()
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if scraper.profiles_scraped:
            scraper.export_to_csv()
    
    finally:
        scraper.close()
    
    print("\n" + "=" * 60)
    print("          SCRAPING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
