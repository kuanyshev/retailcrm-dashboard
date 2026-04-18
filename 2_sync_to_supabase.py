import requests
from datetime import datetime
from config import RETAILCRM_URL, RETAILCRM_API_KEY, SUPABASE_URL

SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6aGluZG91aHdyYnJsbnBiYmJpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0MjMxMjksImV4cCI6MjA5MTk5OTEyOX0.9HiwDM8mriOcMQYz0l31gL6zhsTLQe_1fo7A7aJVQtk"

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON,
    "Authorization": f"Bearer {SUPABASE_ANON}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}


def fetch_all_orders():
    all_orders = []
    page = 1

    while True:
        params = {
            "apiKey": RETAILCRM_API_KEY,
            "limit": 100,
            "page": page
        }

        r = requests.get(f"{RETAILCRM_URL}/api/v5/orders", params=params)
        data = r.json()

        orders = data.get("orders", [])
        all_orders.extend(orders)

        total_pages = data.get("pagination", {}).get("totalPageCount", 1)
        print(f"Страница {page}/{total_pages}")

        if page >= total_pages:
            break
        page += 1

    return all_orders


def upsert_order(order_data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/orders?on_conflict=external_id",
        headers=SUPABASE_HEADERS,
        json=order_data,
    )

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    return r.status_code in (200, 201)


def sync_orders_to_supabase():
    orders = fetch_all_orders()
    print(f"\nВсего заказов: {len(orders)}")

    for order in orders:
        total_sum = 0

        for item in order.get("items", []):
            total_sum += item.get("quantity", 0) * item.get("initialPrice", 0)

        order_data = {
            "external_id": order.get("externalId"),
            "first_name": order.get("firstName"),
            "last_name": order.get("lastName"),
            "phone": order.get("phone"),
            "email": order.get("email"),
            "city": order.get("delivery", {}).get("address", {}).get("city"),
            "total_sum": total_sum,
            "status": order.get("status"),
            "items": order.get("items", []),

            # 🔥 ВАЖНО
            "created_at": order.get("createdAt") or datetime.utcnow().isoformat(),
        }

        upsert_order(order_data)


if __name__ == "__main__":
    sync_orders_to_supabase()