from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(title="SDETFlow Mock Commerce API", version="1.0.0")

VALID_TOKEN = "sdetflow-demo-token"
PRODUCTS = [
    {"id": "p-1001", "name": "Mechanical Keyboard", "price": 299, "stock": 20},
    {"id": "p-1002", "name": "Wireless Mouse", "price": 129, "stock": 35},
]
ORDERS: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class OrderRequest(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, le=10)


def require_token(authorization: str | None) -> None:
    if authorization != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="invalid access token")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict:
    if payload.username != "demo" or payload.password != "sdetflow":
        raise HTTPException(status_code=401, detail="invalid username or password")
    return {"code": 0, "data": {"access_token": VALID_TOKEN, "token_type": "Bearer"}}


@app.get("/api/products")
def products(
    authorization: Annotated[str | None, Header()] = None,
    keyword: Annotated[str | None, Query()] = None,
) -> dict:
    require_token(authorization)
    items = PRODUCTS
    if keyword:
        items = [item for item in items if keyword.lower() in item["name"].lower()]
    return {"code": 0, "data": {"items": items, "total": len(items)}}


@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderRequest, authorization: Annotated[str | None, Header()] = None
) -> dict:
    require_token(authorization)
    product = next((item for item in PRODUCTS if item["id"] == payload.product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    if payload.quantity > product["stock"]:
        raise HTTPException(status_code=409, detail="insufficient stock")
    order_id = f"o-{uuid4().hex[:8]}"
    order = {
        "order_id": order_id,
        "product_id": payload.product_id,
        "quantity": payload.quantity,
        "total_amount": product["price"] * payload.quantity,
        "status": "created",
    }
    ORDERS[order_id] = order
    return {"code": 0, "data": order}


@app.get("/api/orders/{order_id}")
def get_order(
    order_id: str, authorization: Annotated[str | None, Header()] = None
) -> dict:
    require_token(authorization)
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="order not found")
    return {"code": 0, "data": ORDERS[order_id]}

