from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dataclasses import dataclass

@dataclass
class Product:
    """A dataclass to hold the scraped product information."""
    title: str
    price_currency: str
    price_whole: float
    link: str

    def __str__(self):
        return f"{self.title} - {self.price_currency}{self.price_whole} - {self.link}"

def scrape_nykaa_products(product_name: str, browser: webdriver) -> list[Product]:
    """
    Scrapes the main Nykaa website for products and returns a list of Product objects.
    
    Args:
        product_name (str): The product to search for (e.g., "lipstick").
        browser (webdriver): An externally configured Selenium WebDriver instance.
    
    Returns:
        list[Product]: A list of Product objects sorted by price in ascending order.
    """
    try:
        # Navigate to the main Nykaa search page
        query = product_name.replace(" ", "+")
        # Note: The URL is for the main Nykaa beauty site, not Nykaa Fashion
        browser.get(f"https://www.nykaa.com/search/result/?q={query}")
        sleep(5)  # Allow time for the page to load dynamically

        products = []
        # Find all product containers on the page using the new selector
        product_containers = browser.find_elements(by=By.CSS_SELECTOR, value="div.css-ifdzs8")

        for container in product_containers:
            try:
                # Extract the title
                title_element = container.find_element(by=By.CSS_SELECTOR, value="div.css-xrzmfa")
                title = title_element.text.strip()

                # Extract the link from the specific anchor tag
                link_element = container.find_element(by=By.CSS_SELECTOR, value="a.css-qlopj4")
                link = link_element.get_attribute("href") if link_element else ""

                # Extract the discounted price
                # The site has MRP and a final price. We are targeting the final price.
                price_element = container.find_element(by=By.CSS_SELECTOR, value="span.css-111z9ua")
                price_text = price_element.text.replace(",", "").strip("₹")
                
                try:
                    price_whole = float(price_text)
                except ValueError:
                    price_whole = 0.0  # Handle cases where price might not be a number

                price_currency = "₹"

                # Add the product if title and price are valid
                if title and price_whole > 0:
                    product = Product(
                        title=title,
                        price_currency=price_currency,
                        price_whole=price_whole,
                        link=link
                    )
                    products.append(product)
                else:
                    print(f"Skipped product due to missing title or zero price.")

            except NoSuchElementException:
                # This handles cases where a container is an ad or doesn't match the standard product structure
                # print("Skipped a non-standard product container.")
                continue
            except Exception as e:
                # print(f"Could not parse a product container: {e}")
                continue # Move to the next container if another error occurs

        # Sort products by price in ascending order
        products.sort(key=lambda p: p.price_whole)
        return products

    except Exception as e:
        print(f"An error occurred during the Nykaa scraping process: {e}")
        return []
