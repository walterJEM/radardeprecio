from bs4 import BeautifulSoup
from scraper.browser import get_page_html

def scrape_product(url: str) -> dict:
    html = get_page_html(url, wait_for=".ui-pdp-price__second-line")
    soup = BeautifulSoup(html, "lxml")

    name = soup.select_one(".ui-pdp-title")
    image = soup.select_one(".ui-pdp-image")

    # Busca el precio rebajado primero, si no existe agarra el normal
    price_container = soup.select_one(".ui-pdp-price__second-line")
    if not price_container:
        price_container = soup.select_one(".ui-pdp-price__main-container")

    price_text = None
    if price_container:
        fraction = price_container.select_one(".andes-money-amount__fraction")
        cents = price_container.select_one(".andes-money-amount__cents")
        if fraction:
            price_text = fraction.text.strip()
            if cents:
                price_text += "." + cents.text.strip()

    return {
        "url": url,
        "name": name.text.strip() if name else None,
        "price": float(price_text.replace(".", "").replace(",", ".")) if price_text else None,
        "image": image["src"] if image else None,
        "site": "mercadolibre",
    }