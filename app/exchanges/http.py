# app/exchanges/http.py
from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse


def binance_signed_params(params: dict[str, str | int | float], api_secret: str) -> dict[str, str]:
    """
    Binance signed query:
    - add timestamp
    - signature = HMAC_SHA256(querystring, secret)
    """
    p = {k: str(v) for k, v in params.items()}
    p["timestamp"] = str(int(time.time() * 1000))

    query = urllib.parse.urlencode(p)
    signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    p["signature"] = signature
    return p