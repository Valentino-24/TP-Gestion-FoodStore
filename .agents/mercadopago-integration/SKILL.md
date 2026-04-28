---
name: mercadopago-integration
description: |
  Integrate MercadoPago payments in Python/FastAPI. Covers Checkout API, webhooks (IPN), payment preference creation, and webhook HMAC validation.

  Use when implementing e-commerce payments, handling payment callbacks, or configuring MercadoPago as payment provider.
---

# MercadoPago Integration

**Dependencies**: mercadopago (SDK Python), fastapi

---

## Quick Start

```python
from mercadopago import SDK

mp = SDK("ACCESS_TOKEN")
```

---

## Create Payment Preference

```python
preference = mp.preference().create({
    "items": [
        {
            "id": "product-123",
            "title": "Pizza Margherita",
            "quantity": 2,
            "unit_price": 1500.00,
            "currency_id": "ARS"
        }
    ],
    "back_urls": {
        "success": "https://yoursite.com/payment/success",
        "failure": "https://yoursite.com/payment/failure",
        "pending": "https://yoursite.com/payment/pending"
    },
    "external_reference": "ORDER-12345",
    "notification_url": "https://yoursite.com/api/pagos/webhook"
})

checkout_url = preference["response"]["init_point"]
```

---

## Webhook Handler

```python
from fastapi import APIRouter, Request
from mercadopago.helpers import headers as mp_headers
import hmac
import hashlib

router = APIRouter(prefix="/pagos", tags=["pagos"])

@router.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    topic = request.headers.get("x-topic", "").split(".")[0]
    
    if topic == "payment":
        payment_id = data["id"]
        
        # Verify payment status via API
        payment_info = mp.payment().get(payment_id)
        status = payment_info["response"]["status"]
        
        if status == "approved":
            # Update order to CONFIRMADO
            pass
    
    return {"status": "ok"}
```

---

## HMAC Validation (Security)

```python
def verify_webhook_signature(payload: bytes, signature: str, key: str) -> bool:
    expected = hmac.new(
        key.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

---

## Payment Status Flow

| MercadoPago Status | Order State | Action |
|--------------------|-------------|--------|
| pending | PENDIENTE | Wait |
| approved | CONFIRMADO | Decrement stock |
| rejected | PENDIENTE | Keep, show error |
| cancelled | CANCELADO | Cancel order |
| refunded | CANCELADO | Restore stock |

---

## Critical Rules

✅ Use SDK official `mercadopago`
✅ Verify webhook via API (never trust payload alone)
✅ Use `external_reference` to link to your order
✅ Implement idempotency with `idempotency_key`
✅ Never store card data - tokenize client-side
✅ Use TEST credentials for development

---

## Environment Variables

```bash
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxx
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxx
```

---

## Resources

- **MercadoPago Dev Site**: https://www.mercadopago.com.ar/developers
- **Checkout API**: https://www.mercadopago.com.ar/developers/guides/online-payments/checkout-api
- **IPN Guide**: https://www.mercadopago.com.ar/developers/guides/online-payments/ipn