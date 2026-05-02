from bs4 import BeautifulSoup
from scraper.browser import get_page_html

def scrape_product(url: str) -> dict:
    html = get_page_html(url, wait_for=".jsx-3844530124")
    soup = BeautifulSoup(html, "lxml")

    name = soup.select_one(".product-name")
    if not name:
        name = soup.select_one("h1")

    # Busca precio rebajado primero
    price = soup.select_one(".copy10.primary.senary")
    if not price:
        price = soup.select_one("[data-internet-price]")
    if not price:
        price = soup.select_one(".prices-0")

    image = soup.select_one(".photo-slide img")
    if not image:
        image = soup.select_one("img.zoom-image")

    price_text = None
    if price:
        raw = price.get("data-internet-price") or price.text
        price_text = raw.strip().replace("S/", "").replace(".", "").replace(",", ".").strip()

    return {
        "url": url,
        "name": name.text.strip() if name else None,
        "price": float(price_text) if price_text else None,
        "image": image["src"] if image else None,
        "site": "falabella",
    }