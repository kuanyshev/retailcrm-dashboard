import requests
import time
import json
from datetime import datetime, timezone
from config import RETAILCRM_URL, RETAILCRM_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


processed_ids: set = set()
last_check_time: str = ""


def load_state():
    global processed_ids, last_check_time
    try:
        with open('bot_state.json', 'r') as f:
            state = json.load(f)
            processed_ids = set(state.get('ids', []))
            last_check_time = state.get('last_check_time', '')
    except (FileNotFoundError, ValueError):
        processed_ids = set()
        last_check_time = ''


def save_state():
    ids_to_save = list(processed_ids)[-500:]
    with open('bot_state.json', 'w') as f:
        json.dump({'ids': ids_to_save, 'last_check_time': last_check_time}, f)


def send_telegram_message(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False


def check_new_orders():
    global last_check_time

    params = {
        'apiKey': RETAILCRM_API_KEY,
        'limit': 100,
        'page': 1,
    }

    if last_check_time:
        params['filter[createdAtFrom]'] = last_check_time

    try:
        response = requests.get(f"{RETAILCRM_URL}/api/v5/orders", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Ошибка запроса к RetailCRM: {e}")
        return
    except ValueError:
        print(f"Не удалось разобрать ответ RetailCRM")
        return

    orders = data.get('orders', [])

    last_check_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    new_count = 0
    for order in orders:
        order_id = str(order.get('id'))
        external_id = order.get('externalId', '—')

        if order_id in processed_ids:
            continue

        processed_ids.add(order_id)
        new_count += 1

        # Считаем сумму заказа
        total_sum = 0
        for item in order.get('items', []):
            total_sum += item.get('quantity', 0) * item.get('initialPrice', 0)

        if total_sum > 50000:
            message = (
                f"<b>КРУПНЫЙ ЗАКАЗ!</b>\n\n"
                f"Клиент: {order.get('firstName', '')} {order.get('lastName', '')}\n"
                f"Телефон: {order.get('phone', '—')}\n"
                f"Сумма: <b>{total_sum:,.0f} ₸</b>\n"
                f"Заказ №: {external_id}\n\n"
                f"Детали: {RETAILCRM_URL}/orders/{order_id}"
            )
            if send_telegram_message(message):
                print(f"Уведомление отправлено: заказ {external_id} на {total_sum:,.0f} ₸")
            else:
                print(f"Не удалось отправить уведомление для заказа {external_id}")

    if new_count:
        print(f"Обработано новых заказов: {new_count}")
    else:
        print(f"Новых заказов нет ({datetime.now().strftime('%H:%M:%S')})")

    save_state()


if __name__ == "__main__":
    load_state()
    print("Бот запущен. Проверяю заказы каждые 60 секунд...")
    while True:
        try:
            check_new_orders()
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        time.sleep(60)