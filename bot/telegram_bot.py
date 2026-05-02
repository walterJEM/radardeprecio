import requests

TOKEN = "8721637160:AAEW1yLbjKyafDm_X7XVgds7QN4Cr6GWfjc"
CHAT_ID = "2004903676"

def send_message(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def send_alert(product_name: str, site: str, previous: float, current: float, pct: float, url: str):
    message = f"""📉 *Bajada de precio detectada*

🛍 *{product_name}*
🏪 Tienda: {site}
💰 Antes: S/. {previous:,.2f}
✅ Ahora: S/. {current:,.2f}
📊 Bajó: -{pct}%

🔗 {url}"""
    send_message(message)

def send_summary(products: list):
    lines = "\n".join([
        f"• {p['name'][:40]} → S/. {p['last_price']:,.2f} ({p['site']})"
        for p in products
    ])
    message = f"📡 *PriceRadar — Resumen*\n\n{lines}"
    send_message(message)