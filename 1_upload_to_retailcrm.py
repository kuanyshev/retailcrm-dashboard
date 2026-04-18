import requests
import json
from config import RETAILCRM_URL, RETAILCRM_API_KEY


def upload_orders_to_retailcrm():
    with open('mock_orders.json', 'r', encoding='utf-8') as f:
        orders = json.load(f)

    success_count = 0

    for idx, order in enumerate(orders):
        order_data = {
            'externalId': f"MOCK2_{idx + 1}",
            'firstName': order['firstName'],
            'lastName': order['lastName'],
            'phone': order['phone'],
            'email': order['email'],
            'orderType': 'main',
            'orderMethod': order['orderMethod'],
            'status': order['status'],
            'items': [],
            'delivery': order['delivery'],
            'customFields': order['customFields'],
        }

        total_sum = 0
        for item in order.get('items', []):
            order_data['items'].append({
                'offer': {'externalId': item['productName']},
                'quantity': item['quantity'],
                'initialPrice': item['initialPrice'],
            })
            total_sum += item['quantity'] * item['initialPrice']

        order_data['totalSumm'] = total_sum

        url = f"{RETAILCRM_URL}/api/v5/orders/create"

        payload = {
            'apiKey': RETAILCRM_API_KEY,
            'order': json.dumps(order_data),
        }

        try:
            response = requests.post(url, data=payload)
            result = response.json()
            print(f"Статус: {response.status_code}, Ответ: {result}")
            if response.status_code in (200, 201) and result.get('success'):
                success_count += 1
                print(f"Заказ {idx + 1} загружен (id={result.get('id')})")
            else:
                print(f"Ошибка заказа {idx + 1}: {result}")

        except requests.RequestException as e:
            print(f"Сетевая ошибка на заказе {idx + 1}: {e}")
        except ValueError:
            print(f"Не удалось разобрать ответ на заказе {idx + 1}: {response.text}")

    print(f"\nЗагружено {success_count} из {len(orders)} заказов")


if __name__ == "__main__":
    upload_orders_to_retailcrm()