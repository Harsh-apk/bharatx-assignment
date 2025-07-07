from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from dataclasses import dataclass

@dataclass
class Product:
    title: str
    price_currency: str
    price_whole: float
    link: str

    def __str__(self):
        return f"{self.title} - {self.price_currency}{self.price_whole} - {self.link}"

def scrape_flipkart_products(product_name: str, browser: webdriver) -> list[Product]:
    """
    Scrape Flipkart for products matching the product_name and return a sorted list of Product objects.
    
    Args:
        product_name (str): The product to search for (e.g., "iphone 16 pro max").
        browser (webdriver): Selenium WebDriver instance (configured externally).
    
    Returns:
        list[Product]: A list of Product objects sorted by price_whole in ascending order.
    """
    try:
        # Navigate to Flipkart search page
        query = product_name.replace(" ", "+")
        browser.get(f"https://www.flipkart.com/search?q={query}")
        sleep(5)  # Wait for page to load

        products = []
        product_containers = browser.find_elements(by=By.CSS_SELECTOR, value="div.yKfJKb.row")

        for container in product_containers:
            try:
                # Extract title
                title_element = container.find_element(by=By.CSS_SELECTOR, value="div.KzDlHZ")
                title = title_element.text.strip() if title_element else ""

                # Extract price
                price_whole_element = container.find_element(by=By.CSS_SELECTOR, value="div.Nx9bqj._4b5DiR")
                price_whole_text = price_whole_element.text.replace(",", "").strip("₹") if price_whole_element else "0"
                try:
                    price_whole = float(price_whole_text)
                except ValueError:
                    price_whole = 0.0  # Handle non-numeric prices (e.g., "Out of Stock")
                price_currency = "₹"

                # Extract link (updated to find <a> containing the title)
                try:
                    link_element = container.find_element(by=By.XPATH, value=".//a[.//div[@class='KzDlHZ']]")
                    link = link_element.get_attribute("href") if link_element else ""
                except:
                    link = ""  # Set empty link if not found

                # Add product if title and price are valid (link is optional)
                if title and price_whole > 0:
                    product = Product(
                        title=title,
                        price_currency=price_currency,
                        price_whole=price_whole,
                        link=link
                    )
                    products.append(product)
                    # print(f"Added: {title} - {price_whole} - {link}")
                else:
                    print(f"Skipped (invalid title or price): {title} - {price_whole}")

            except Exception as e:
                print(f"Error parsing product container: {e}")
                continue

        # Sort products by price
        products.sort(key=lambda x: x.price_whole)
        return products

    except Exception as e:
        print(f"Error during Flipkart scraping: {e}")
        return []