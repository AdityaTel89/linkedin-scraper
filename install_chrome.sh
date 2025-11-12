#!/bin/bash

# Install Chrome dependencies
apt-get update
apt-get install -y wget gnupg

# Add Chrome repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - 2>/dev/null || \
wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install Chrome
if [ -f /tmp/chrome.deb ]; then
    apt-get install -y /tmp/chrome.deb
    rm /tmp/chrome.deb
else
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
fi

# Verify installation
google-chrome --version
