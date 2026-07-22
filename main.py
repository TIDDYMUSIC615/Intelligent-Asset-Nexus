import os
import json
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()

SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "changeme")


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_api_key: Optional[str] = Header(None),
):
    if x_api_key != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    action = payload.get("action")
    symbol = payload.get("symbol")
    order_type = payload.get("order_type")
    quantity = payload.get("quantity")

    if not all([action, symbol, order_type, quantity]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    trade_command = {
        "action": action,
        "symbol": symbol,
        "order_type": order_type,
        "quantity": quantity,
    }

    print(json.dumps(trade_command, indent=2))

    return {"status": "ok"}
