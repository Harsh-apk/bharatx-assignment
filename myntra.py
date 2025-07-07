from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from urllib.parse import urljoin
from selenium.common.exceptions import NoSuchElementException

@dataclass
class Product:
    """A class to hold product information."""
    title: str
    price_currency: str
    price_whole: float
    link: str

    def __str__(self):
        return f"{self.title} - {self.price_currency} {self.price_whole} - {self.link}"

def scrape_myntra_products(product_name: str, browser: webdriver) -> list[Product]:
    """
    Scrapes Myntra for products matching the product_name and returns a sorted list of Product objects.

    Args:
        product_name (str): The product to search for (e.g., "iphone 16 pro max").
        browser (webdriver): The Selenium WebDriver instance.

    Returns:
        list[Product]: A list of Product objects sorted by price in ascending order.
    """
    try:
        # Navigate to Myntra's search page
        base_url = "https://www.myntra.com/"
        query = product_name.replace(" ", "-")
        browser.get(f"{base_url}{query}")

        # Wait for the product containers to be present
        wait = WebDriverWait(browser, 5)
        product_containers = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.product-base"))
        )

        products = []
        for container in product_containers:
            try:
                # Extract the product brand and name to create a full title
                brand_element = container.find_element(By.CSS_SELECTOR, "h3.product-brand")
                product_element = container.find_element(By.CSS_SELECTOR, "h4.product-product")
                title = f"{brand_element.text.strip()} {product_element.text.strip()}"

                # Extract the product price
                try:
                    # Myntra may show a discounted price or a regular price
                    price_element = container.find_element(By.CSS_SELECTOR, "span.product-discountedPrice")
                except NoSuchElementException:
                    # If no discounted price, look for the standard price
                    price_element = container.find_element(By.CSS_SELECTOR, "div.product-price")
                
                price_text = price_element.text.replace("Rs.", "").replace(",", "").strip()
                price_whole = float(price_text)
                price_currency = "Rs."

                # Extract the product link and make it absolute
                link_element = container.find_element(By.TAG_NAME, "a")
                relative_link = link_element.get_attribute("href")
                link = urljoin(base_url, relative_link)

                # Add valid products to the list
                if title and price_whole > 0:
                    products.append(Product(
                        title=title,
                        price_currency=price_currency,
                        price_whole=price_whole,
                        link=link
                    ))
            except Exception as e:
                # This handles cases where a container might be an ad or otherwise empty
                # print(f"Could not parse a product container: {e}")
                continue

        # Sort products by price
        products.sort(key=lambda p: p.price_whole)
        return products

    except Exception as e:
        print(f"An error occurred while scraping Myntra: {e}")
        return []

