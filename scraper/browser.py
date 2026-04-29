from playwright.sync_api import sync_playwright
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_page_html(url: str, wait_for: str = None) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # visible para evitar detección
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            locale="es-PE",
            timezone_id="America/Lima",
        )

        # Oculta que es Playwright
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = context.new_page()

        # Espera aleatoria antes de cargar
        time.sleep(random.uniform(1, 3))

        page.goto(url, timeout=60000, wait_until="domcontentloaded")

        if wait_for:
            try:
                page.wait_for_selector(wait_for, timeout=15000)
            except:
                pass  # continúa aunque no encuentre el selector

        # Scroll para simular comportamiento humano
        page.evaluate("window.scrollTo(0, 300)")
        time.sleep(random.uniform(1, 2))

        html = page.content()
        browser.close()
        return html