from fastapi import FastAPI, HTTPException

from db.models import get_price_history_by_id, get_all_products
app = FastAPI(title="PriceRadar API", version="1.0")

@app.get("/")
def root():
    return {"status": "ok", "message": "PriceRadar API corriendo"}

@app.get("/products")
def list_products():
    products = get_all_products()
    if not products:
        return {"products": [], "total": 0}
    return {"products": products, "total": len(products)}

@app.get("/products/{product_id}/history")
def price_history(product_id: int):
    history = get_price_history_by_id(product_id)
    if not history:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"product_id": product_id, "history": history}