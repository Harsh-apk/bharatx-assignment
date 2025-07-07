from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from dataclasses import dataclass
from selenium.webdriver.chrome.options import Options
from amazon import scrape_amazon_products 
from flipkart import scrape_flipkart_products
from target import scrape_target_products
from myntra import scrape_myntra_products
from nykaa import scrape_nykaa_products
# Define a Product class using dataclass for simplicity
@dataclass
class Product:
    title: str
    price_currency: str
    price_whole: float
    link: str

    def __str__(self):
        return f"{self.title} - {self.price_currency}{self.price_whole} - {self.link}"

# Initialize the WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless
# chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
# chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
service = Service(executable_path="chromedriver-mac-arm64/chromedriver")  # Replace with your path
browser = webdriver.Chrome(service=service,options=chrome_options)

# prods = scrape_amazon_products("iphone 16 pro max", browser)
# prods = scrape_flipkart_products("iphone 16 pro max", browser)
# prods = scrape_target_products("iphone 16 pro max", browser)
# prods = scrape_myntra_products("lipstick", browser)
prods = scrape_nykaa_products("lipstick", browser)


for prod in prods:
    print(prod.price_whole)
# Close the browser
browser.quit()