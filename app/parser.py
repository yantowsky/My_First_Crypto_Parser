# app/parser.py


def extract_products(data: dict) -> list:
    return data.get("result", {}).get("list", [])


def detect_new_and_update_state(products: list, state: dict) -> list:
    """
    Alert conditions (ONLY):
      1) new productId
      2) status changed to Available (transition into Available)
    """
    alerts = []

    for p in products:
        product_id = p.get("productId")
        if not product_id:
            continue

        status = p.get("status")
        prev = state.get(product_id)

        is_new = prev is None
        became_available = (prev is not None and prev.get("status") != "Available" and status == "Available")

        if is_new or became_available:
            alerts.append(p)

        state[product_id] = {
            "status": status,
            "coin": p.get("coin"),
            "term": p.get("term"),
            "category": p.get("category"),
        }

    return alerts
