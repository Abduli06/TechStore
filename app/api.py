from fastapi import FastAPI, HTTPException, Query
from cargar_csv import load_fixture
from app.domain import InvalidOrderTransition, InvalidOrderData

app = FastAPI(title="TechStore API")
orders = load_fixture()

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return {
        "id": order.id,
        "status": order.status.value,
        "units": order.units,
        "total": str(order.total.amount)
    }

@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        order.confirm()
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value, "detail": "El pedido ha sido confirmado"}

@app.post("/orders/{order_id}/ship")
def ship_order(order_id: str, tracking_number: str = Query(..., description="Número de guía de envío")):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        order.ship(tracking_number)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value, "detail": "El pedido ya va en camino" }

@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, reason: str = Query(..., description="Motivo de la cancelación")):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        order.cancel(reason)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value, "detail": "El pedido ha sido cancelado"}