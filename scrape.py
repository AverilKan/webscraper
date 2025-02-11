'scrape.py: A module to scrape a website and extract body content.'

import os
import json
import logging
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_website(url, wait_time=10):
    """Launch Chrome, fetch page source, and close browser safely."""
    logging.info(f"Launching browser for {url}...")

    chrome_driver_path = './chromedriver.exe'
    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError("ChromeDriver not found! Check path or install it.")

    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Prevents rendering issues
    options.add_argument("--no-sandbox")  # Helps with stability
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in containers

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logging.info("Scraping completed successfully.")
        return driver.page_source

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return None

    finally:
        driver.quit()
        logging.info("Browser closed.")

def extract_body_content(html_content):
    """Extract and return clean body content."""
    if not html_content:
        raise ValueError("Error: Received empty or None HTML content.")

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted tags
    for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
        tag.extract()

    return soup.get_text(separator=' ', strip=True)

def clean_body_content(body_content):
    """Remove extra spaces and clean up content."""
    if not body_content:
        return ""

    # Remove extra whitespace, blank lines, and special characters
    clean_content = '\n'.join(line.strip() for line in body_content.splitlines() if line.strip())
    
    return clean_content

def split_content(dom_content, max_length=25000):
    """
    Merges extracted content into larger chunks before sending to the LLM.
    """
    words = dom_content.split()
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(word) < max_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return ["\n".join(chunks)] 

def save_to_json(data, filename="scraped_data.json"):
    """Save extracted data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"Data saved to {filename}")


