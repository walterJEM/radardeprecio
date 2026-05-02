from config import get_active_urls, get_scraper_settings
from scraper.sites.mercadolibre import scrape_product
from db.models import save_price, init_db, detect_price_drop
from scraper.sites.falabella import scrape_product as scrape_falabella

import time

SCRAPERS = {
    "mercadolibre": scrape_product,
    "falabella": scrape_falabella,
}

if __name__ == "__main__":
    init_db()
    urls = get_active_urls()
    settings = get_scraper_settings()

    print(f"Scrapeando {len(urls)} productos...\n")

    for site in urls:
        scraper_fn = SCRAPERS.get(site["site"])
        if not scraper_fn:
            continue
        try:
            product = scraper_fn(site["url"])
            save_price(product)
            print(f"OK  {site['name']} → S/. {product['price']}")

            drop = detect_price_drop(site["url"])
            if drop:
                print(f"    BAJADA: S/. {drop['previous']} → S/. {drop['current']} (-{drop['pct']}%)")

        except Exception as e:
            print(f"ERR {site['name']}: {e}")

        time.sleep(settings["delay_seconds"])