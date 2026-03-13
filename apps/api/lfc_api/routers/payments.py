import hmac
import hashlib
import json
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from lfc_api.core import config
from lfc_api.core.deps import get_current_user
from lfc_api.core.ticketing import issue_ticket_for_order
from lfc_api.db.session import get_db
from lfc_api.models.ticketing import Order
from lfc_api.models.user import User

router = APIRouter(prefix="/payments", tags=["payments"])


class CloverCheckoutIn(BaseModel):
    order_id: str


def _require_admin_or_owner(current_user: User, order: Order):
    if current_user.role == "admin":
        return
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")


def _verify_clover_signature(signature_header: str, raw_body: bytes) -> bool:
    try:
        parts = {}
        for item in signature_header.split(","):
            k, v = item.split("=", 1)
            parts[k.strip()] = v.strip()

        timestamp = parts["t"]
        sent_signature = parts["v1"]
    except Exception:
        return False

    signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode("utf-8")

    expected = hmac.new(
        config.CLOVER_WEBHOOK_SECRET.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, sent_signature)


@router.post("/clover/checkout")
def create_clover_checkout(
    data: CloverCheckoutIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    _require_admin_or_owner(current_user, order)

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order is not pending")

    if not config.CLOVER_API_TOKEN:
        raise HTTPException(status_code=500, detail="Clover API token not configured")

    if not config.CLOVER_MERCHANT_ID:
        raise HTTPException(status_code=500, detail="Clover merchant id not configured")

    base_url = getattr(config, "CLOVER_BASE_URL", "").strip()
    if not base_url:
        raise HTTPException(status_code=500, detail="Clover base URL not configured")

    payload = {
        "customer": {},
        "shoppingCart": {
            "lineItems": [
                {
                    "name": f"Ticket {order.ticket_type_id}",
                    "price": order.total_cents,
                    "unitQty": 1,
                }
            ]
        },
        "redirectUrls": {
            "success": config.CLOVER_SUCCESS_URL,
            "cancel": config.CLOVER_CANCEL_URL,
        },
        "note": f"LFC order {order.id}",
        "externalReferenceId": order.id,
    }

    headers = {
        "Authorization": f"Bearer {config.CLOVER_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{base_url}/v1/checkouts",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Clover request failed: {str(e)}")

    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Clover error: {resp.text}")

    response_data = resp.json()

    checkout_id = response_data.get("id") or response_data.get("checkoutSessionId")
    checkout_url = (
        response_data.get("href")
        or response_data.get("checkoutUrl")
        or response_data.get("url")
    )

    if not checkout_id or not checkout_url:
        raise HTTPException(
            status_code=502,
            detail="Clover response missing checkout id or URL",
        )

    order.clover_checkout_id = str(checkout_id)
    db.commit()
    db.refresh(order)

    return {
        "ok": True,
        "order_id": order.id,
        "clover_checkout_id": order.clover_checkout_id,
        "checkout_url": checkout_url,
    }


@router.post("/clover/webhook")
async def clover_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    signature = request.headers.get("Clover-Signature", "")

    if not config.CLOVER_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Clover webhook secret not configured")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing Clover-Signature header")

    if not _verify_clover_signature(signature, raw_body):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    order_id = (
        payload.get("externalReferenceId")
        or payload.get("order_id")
        or payload.get("referenceId")
    )

    payment_id = payload.get("paymentId") or payload.get("id")
    payment_status = (
        payload.get("status")
        or payload.get("paymentStatus")
        or payload.get("result")
    )

    amount = (
        payload.get("amount")
        or payload.get("total")
        or payload.get("totalAmount")
    )

    if not order_id:
        raise HTTPException(status_code=400, detail="Missing order reference in webhook")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    normalized_status = str(payment_status).lower()
    if normalized_status not in {"approved", "paid", "succeeded", "success"}:
        return {
            "ok": True,
            "order_id": order.id,
            "status": order.status,
            "ignored": True,
        }

    if amount is not None:
        try:
            paid_amount = int(amount)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid payment amount")

        if paid_amount != order.total_cents:
            raise HTTPException(status_code=400, detail="Payment amount mismatch")

    if payment_id:
        order.clover_payment_id = str(payment_id)

    if order.status != "paid":
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)

    ticket = issue_ticket_for_order(db, order)
    db.commit()
    db.refresh(order)
    db.refresh(ticket)

    return {
        "ok": True,
        "order_id": order.id,
        "status": order.status,
        "ticket_id": ticket.id,
        "qr_token": ticket.qr_token,
    }
