from config import get_active_urls, get_scraper_settings
from scraper.sites.mercadolibre import scrape_product as scrape_mercadolibre
from scraper.sites.falabella import scrape_product as scrape_falabella
from db.models import save_price, init_db, detect_price_drop, get_all_products
from bot.telegram_bot import send_alert, send_summary
import time

SCRAPERS = {
    "mercadolibre": scrape_mercadolibre,
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
                send_alert(
                    product_name=product["name"],
                    site=site["site"],
                    previous=drop["previous"],
                    current=drop["current"],
                    pct=drop["pct"],
                    url=site["url"]
                )
        except Exception as e:
            print(f"ERR {site['name']}: {e}")

        time.sleep(settings["delay_seconds"])

    # Resumen final
    send_summary(get_all_products())
    print("\nResumen enviado por Telegram.")