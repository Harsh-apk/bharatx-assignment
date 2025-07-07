import concurrent.futures
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dataclasses import asdict

# Assuming your scraper functions are in separate files as indicated
# Create these files (amazon.py, flipkart.py, etc.) in the same directory
from amazon import scrape_amazon_products
from flipkart import scrape_flipkart_products
from target import scrape_target_products
from myntra import scrape_myntra_products
from nykaa import scrape_nykaa_products

app = Flask(__name__)

# --- WebDriver Initialization ---
def initialize_browser():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path="chromedriver-mac-arm64/chromedriver")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser
# --- Scraper Mapping ---
# A list of all available scraper functions
ALL_SCRAPERS = [
    scrape_amazon_products,
    scrape_flipkart_products,
    scrape_target_products,
    scrape_myntra_products,
    scrape_nykaa_products,
]

def run_scraper(scraper_function, product_name):
    """
    Initializes a browser, runs a single scraper function, and cleans up.
    This function is designed to be run in a separate thread.
    """
    browser = None
    try:
        browser = initialize_browser()
        products = scraper_function(product_name, browser)
        return products
    except Exception as e:
        # Log the error for the specific scraper
        print(f"Error in {scraper_function.__name__}: {e}")
        return [] # Return an empty list if a scraper fails
    finally:
        if browser:
            browser.quit()


@app.route('/search', methods=['GET'])
def search_products():
    """
    API endpoint to scrape products from all available websites.
    Query Parameters:
        - product_name (str): The name of the product to search for.
        - location (str, optional): The country for the search (e.g., 'us', 'india'). Currently ignored.
    Returns:
        A single JSON list of all found products, sorted by price.
    """
    product_name = request.args.get('product_name')
    # Location is accepted but not used in the logic for now, as requested.
    location = request.args.get('location') 

    # --- Input Validation ---
    if not product_name:
        return jsonify({"error": "'product_name' query parameter is required."}), 400

    all_products = []
    # --- Concurrent Scraping Logic ---
    # Use a ThreadPoolExecutor to run all scrapers in parallel for better performance.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a future for each scraper function
        future_to_scraper = {executor.submit(run_scraper, scraper, product_name): scraper for scraper in ALL_SCRAPERS}
        for future in concurrent.futures.as_completed(future_to_scraper):
            try:
                # Get the result from the completed future
                result = future.result()
                if result:
                    all_products.extend(result)
            except Exception as exc:
                scraper_name = future_to_scraper[future].__name__
                print(f'{scraper_name} generated an exception: {exc}')

    # --- Sorting and Formatting ---
    # Sort the combined list of all products by price in ascending order
    all_products.sort(key=lambda p: p.price_whole)

    # Convert the list of Product objects to a list of dictionaries for the JSON response
    products_dict = [asdict(p) for p in all_products]
    
    return jsonify(products_dict)

if __name__ == '__main__':
    # For production, use a proper WSGI server like Gunicorn or uWSGI
    app.run(debug=True, port=5001)
