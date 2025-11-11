# 🔗 LinkedIn Profile Scraper

A professional web-based tool for extracting LinkedIn profile data with a modern UI and automated scraping capabilities.

## ✨ Features

- 🎨 Modern, responsive web interface
- 🚀 Automated profile data extraction
- 📊 Real-time progress tracking
- 💾 CSV export functionality
- 🔒 Secure credential handling
- 📈 Success/failure statistics
- 🎯 Rate limiting and anti-detection measures

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- LinkedIn account

## 🚀 Quick Start

### 1. Clone or Download

cd linkedin-scraper


### 2. Create Virtual Environment

python -m venv venv

Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Configure Environment

Copy `.env.example` to `.env` and add your credentials:

cp .env.example .env

Edit `.env`:

LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password

### 5. Run the Application

python app.py

Open your browser and navigate to: [**http://localhost:5000**](http://localhost:5000)


## 🎯 Usage

1. **Start the application** using `python app.py`
2. **Open the web interface** at http://localhost:5000
3. **Enter your LinkedIn credentials**
4. **Add profile URLs** (one per line)
5. **Click "Start Scraping"**
6. **Monitor progress** in real-time
7. **Download CSV** when complete

## 📊 Extracted Data

The scraper extracts the following profile information:

- Full name
- Professional headline
- Location
- About section
- Current position/company
- Profile URL

## ⚙️ Configuration

Key settings in `.env`:

MIN_DELAY=30 # Minimum delay between profiles (seconds)
MAX_DELAY=90 # Maximum delay between profiles (seconds)
LONG_BREAK=180 # Long break duration (seconds)
HEADLESS_MODE=False # Run browser in headless mode

## 🔒 Security Notes

- Never commit `.env` file to version control
- Keep your LinkedIn credentials secure
- Use environment variables for sensitive data
- Respect LinkedIn's rate limits and terms of service

## ⚠️ Important Warnings

- This tool is for educational purposes only
- Scraping LinkedIn may violate their Terms of Service
- Use responsibly and at your own risk
- LinkedIn may block accounts that scrape aggressively
- Consider using LinkedIn's official API for production use

## 🐛 Troubleshooting

### Chrome Driver Issues
pip install --upgrade selenium

### Login Failures
- Verify credentials in `.env` file
- Check if LinkedIn requires 2FA
- Manually complete CAPTCHA if prompted

### Rate Limiting
- Increase delays in `.env` file
- Reduce number of profiles per session
- Use residential proxies (optional)

## 📝 Output Format

CSV file with columns:
- `name` - Profile name
- `headline` - Professional headline
- `location` - Geographic location
- `current_position` - Current job/company
- `about` - About section text
- `url` - Profile URL

## 🛠️ Development

Run in development mode:

Set in .env
FLASK_ENV=development
FLASK_DEBUG=True

python app.py

## 📄 License

This project is for educational purposes only. Use at your own risk.

## 🤝 Contributing

This is a personal project. Feel free to fork and modify for your own use.

## 📧 Support

For issues or questions, please check the troubleshooting section above.

---

**Built with Flask, Selenium, and Modern Web Technologies** 🚀


