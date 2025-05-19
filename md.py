import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import quote

# Initialize result storage as a list of dictionaries
results = {
    "products": []  # Each item will be a dict with name, price, old_price, and image
}

# Throttler setup
RPM_LIMIT = 200
REQUEST_DELAY = 60 / RPM_LIMIT  # Delay per request (in seconds)
SEMAPHORE = asyncio.Semaphore(RPM_LIMIT)  # To limit concurrency


async def fetch_page(session: ClientSession, url: str):
    """
    Fetch a single page asynchronously with rate limiting.
    """
    async with SEMAPHORE:
        async with session.get(url) as response:
            return await response.text()


async def parse_page(session: ClientSession, url: str):
    """
    Fetch and parse the product data from a single page.
    """
    html_content = await fetch_page(session, url)
    soup = BeautifulSoup(html_content, features="html.parser")
    data = soup.find('div', class_='-pvs col12')

    if not data:
        return []

    # Extract and combine product details
    products = []
    names = data.find_all('h3', class_='name')
    prices = data.find_all('div', class_='prc')
    old_prices = data.find_all('div', class_='old')
    images = data.find_all('img', class_='img')

    # Zip all product details together
    for name, price, old_price, image in zip(names, prices, old_prices, images):
        product = {
            "name": name.text if name else None,
            "price": price.text if price else None,
            "old_price": old_price.text if old_price else None,
            "image": image.get('data-src') if image else None
        }
        products.append(product)

    return products


async def scrape_pages(query: str, pages: int):
    """
    Scrape multiple pages concurrently while respecting the rate limit.
    """
    base_url = "https://www.jumia.com.ng/catalog/?q={query}&page={page}#catalog-listing"
    tasks = []
    async with ClientSession() as session:
        for i in range(1, pages + 1):
            # Properly encode the query parameter
            encoded_query = quote(query)
            url = base_url.format(query=encoded_query, page=i)
            tasks.append(parse_page(session, url))
            await asyncio.sleep(REQUEST_DELAY)  # Respect rate limit

        # Gather results from all tasks
        responses = await asyncio.gather(*tasks)

    # Combine results
    for products in responses:
        results["products"].extend(products)


def main(query: str, pages: int):
    """
    Main function to run the scraper and print results.
    """
    # Clear previous results
    results["products"].clear()

    # Run the async scraper
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_pages(query, pages))

    # Display the results
    print("Scraping completed. Here are the results:")
    print("Products:", results["products"])


# Example Usage
if __name__ == "__main__":
    # Replace 'laptop' and '3' with your desired query and number of pages
    main(query="laptop", pages=3)
