from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from db.models import get_price_history_by_id, get_all_products
from datetime import datetime
from collections import defaultdict
from pathlib import Path

app = FastAPI(title="PriceRadar API", version="1.0")

@app.get("/", response_class=HTMLResponse)
def dashboard():
    products = get_all_products()

    by_name = defaultdict(list)
    for p in products:
        key = p["name"][:30]
        by_name[key].append(p)

    for group in by_name.values():
        prices = [p["last_price"] for p in group if p["last_price"]]
        if prices:
            min_price = min(prices)
            for p in group:
                p["is_lowest"] = p["last_price"] == min_price

    history_data = []
    for p in products:
        h = get_price_history_by_id(p["id"])
        if h:
            history_data.append({
                "name": p["name"],
                "site": p["site"],
                "history": h["history"]
            })

    import json
    history_json = json.dumps(history_data)
    last_updated = datetime.now().strftime("%d/%m %H:%M")
    sites = set(p["site"] for p in products)
    drops = sum(1 for p in products if p.get("is_lowest"))

    rows = ""
    for p in products:
        lowest_mark = "✅" if p.get("is_lowest") else ""
        price_class = "price-low" if p.get("is_lowest") else ""
        name = p["name"][:50] + "..." if len(p["name"]) > 50 else p["name"]
        rows += f"""
        <tr>
            <td>{name}</td>
            <td><span class="site-badge {p['site']}">{p['site']}</span></td>
            <td class="price {price_class}">S/. {p['last_price']:,.2f} {lowest_mark}</td>
            <td style="color:#aaa;font-size:13px;">{p['last_scraped'][:10]}</td>
            <td><a href="{p['url']}" target="_blank">↗</a></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PriceRadar</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:system-ui,sans-serif; background:#f5f5f5; color:#333; }}
        header {{ background:#1a1a2e; color:white; padding:1.5rem 2rem; display:flex; align-items:center; gap:12px; }}
        header h1 {{ font-size:1.5rem; font-weight:600; }}
        .container {{ max-width:1100px; margin:2rem auto; padding:0 1.5rem; }}
        .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin-bottom:2rem; }}
        .stat-card {{ background:white; border-radius:12px; padding:1.25rem 1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
        .stat-card .label {{ font-size:12px; color:#888; margin-bottom:4px; }}
        .stat-card .value {{ font-size:1.75rem; font-weight:700; color:#1a1a2e; }}
        .stat-card .sub {{ font-size:12px; color:#aaa; margin-top:2px; }}
        .card {{ background:white; border-radius:12px; padding:1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); margin-bottom:1.5rem; }}
        .card h2 {{ font-size:1rem; font-weight:600; margin-bottom:1rem; color:#1a1a2e; }}
        table {{ width:100%; border-collapse:collapse; font-size:14px; }}
        th {{ text-align:left; padding:10px 12px; background:#f9f9f9; color:#666; font-weight:500; border-bottom:1px solid #eee; }}
        td {{ padding:12px; border-bottom:1px solid #f0f0f0; }}
        tr:last-child td {{ border-bottom:none; }}
        tr:hover td {{ background:#fafafa; }}
        .site-badge {{ display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:500; }}
        .mercadolibre {{ background:#fff3d0; color:#b8860b; }}
        .falabella {{ background:#ffe0e0; color:#c0392b; }}
        .price {{ font-weight:700; font-size:1rem; color:#1a1a2e; }}
        .price-low {{ color:#27ae60; }}
        .chart-container {{ position:relative; height:280px; }}
        .product-selector {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem; }}
        .product-btn {{ padding:6px 14px; border:1.5px solid #ddd; border-radius:20px; background:white; cursor:pointer; font-size:13px; transition:all 0.15s; }}
        .product-btn.active {{ border-color:#1a1a2e; background:#1a1a2e; color:white; }}
        a {{ color:#1a1a2e; text-decoration:none; }}
    </style>
</head>
<body>
<header><span>📡</span><h1>PriceRadar</h1></header>
<div class="container">
    <div class="stats">
        <div class="stat-card">
            <div class="label">Productos monitoreados</div>
            <div class="value">{len(products)}</div>
            <div class="sub">en {len(sites)} tiendas</div>
        </div>
        <div class="stat-card">
            <div class="label">Última actualización</div>
            <div class="value" style="font-size:1.1rem;margin-top:6px;">{last_updated}</div>
        </div>
        <div class="stat-card">
            <div class="label">Precios más bajos detectados</div>
            <div class="value" style="color:#27ae60;">{drops}</div>
        </div>
    </div>
    <div class="card">
        <h2>📊 Comparación de precios</h2>
        <table>
            <thead>
                <tr>
                    <th>Producto</th><th>Tienda</th><th>Precio actual</th><th>Fecha</th><th>Ver</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    <div class="card">
        <h2>📈 Historial de precios</h2>
        <div class="product-selector" id="selector"></div>
        <div class="chart-container"><canvas id="priceChart"></canvas></div>
    </div>
</div>
<script>
const historyData = {history_json};
let chart = null;
function buildSelector() {{
    const sel = document.getElementById('selector');
    historyData.forEach((p, i) => {{
        const btn = document.createElement('button');
        btn.className = 'product-btn' + (i === 0 ? ' active' : '');
        btn.textContent = p.name.substring(0, 30) + (p.name.length > 30 ? '...' : '');
        btn.onclick = () => {{
            document.querySelectorAll('.product-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderChart(p);
        }};
        sel.appendChild(btn);
    }});
    if (historyData.length > 0) renderChart(historyData[0]);
}}
function renderChart(product) {{
    const labels = product.history.map(h => h.scraped_at.substring(0, 10));
    const prices = product.history.map(h => h.price);
    if (chart) chart.destroy();
    chart = new Chart(document.getElementById('priceChart'), {{
        type: 'line',
        data: {{
            labels,
            datasets: [{{
                label: 'Precio S/.',
                data: prices,
                borderColor: '#1a1a2e',
                backgroundColor: 'rgba(26,26,46,0.06)',
                borderWidth: 2,
                pointRadius: 5,
                pointBackgroundColor: '#1a1a2e',
                tension: 0.3,
                fill: true,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{ y: {{ ticks: {{ callback: v => 'S/. ' + v.toLocaleString() }} }} }}
        }}
    }});
}}
buildSelector();
</script>
</body>
</html>"""

    return HTMLResponse(content=html)

@app.get("/api/products")
def list_products():
    products = get_all_products()
    return {"products": products, "total": len(products)}

@app.get("/api/products/{product_id}/history")
def price_history(product_id: int):
    history = get_price_history_by_id(product_id)
    if not history:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"product_id": product_id, "history": history}