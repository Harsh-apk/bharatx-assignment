from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from dataclasses import dataclass

# Define a Product class using dataclass
@dataclass
class Product:
    title: str
    price_currency: str
    price_whole: float
    link: str

    def __str__(self):
        return f"{self.title} - {self.price_currency}{self.price_whole} - {self.link}"

def scrape_amazon_products(product_name: str, browser: webdriver) -> list[Product]:
    """
    Scrape Amazon for products matching the product_name and return a sorted list of Product objects.
    
    Args:
        product_name (str): The product to search for (e.g., "iphone 16 pro max").
        chromedriver_path (str): Path to the chromedriver executable.
    
    Returns:
        list[Product]: A list of Product objects sorted by price_whole in ascending order.
    """



        # Navigate to Amazon search page
    query = product_name.replace(" ", "+")
    browser.get(f"https://www.amazon.in/s?k={query}")
    sleep(5)

        # Initialize list to store products
    products = []

        # Find all product containers
    product_containers = browser.find_elements(by=By.CSS_SELECTOR, value="div.s-result-item")

    for container in product_containers:
        try:
                # Extract title
            title_element = container.find_element(by=By.CSS_SELECTOR, value="h2.a-size-medium.a-text-normal span")
            title = title_element.text.strip() if title_element else ""

                # Extract price
            price_whole_element = container.find_element(by=By.CSS_SELECTOR, value="span.a-price-whole")
            price_whole = float(price_whole_element.text.replace(",", "").strip()) if price_whole_element else 0.0

            price_currency_element = container.find_element(by=By.CSS_SELECTOR, value="span.a-price-symbol")
            price_currency = price_currency_element.text.strip() if price_currency_element else "₹"

                # Extract link
            link_element = container.find_element(by=By.CSS_SELECTOR, value="a.a-link-normal.a-text-normal")
            link = link_element.get_attribute("href") if link_element else ""

                # Create Product instance and add to list
            if title and price_whole > 0:  # Only add valid products
                product = Product(
                    title=title,
                    price_currency=price_currency,
                    price_whole=price_whole,
                    link=link
                )
                products.append(product)

        except Exception as e:
                print(f"Error parsing product container: {e}")
                continue

        # Sort products by price_whole in ascending order
    products.sort(key=lambda x: x.price_whole)

    return products