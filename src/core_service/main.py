from binance import ThreadedWebsocketManager

from src.core_service.settings import API_KEY, API_SECRET

api_key = API_KEY
api_secret = API_SECRET


def handle_socket_message(msg):
    event_time = msg['E']
    current_price = msg['c']

    print(f"Время события: {event_time}, Текущая цена {msg['s']}: {current_price}")


twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=True)
twm.start()

twm.start_symbol_ticker_socket(callback=handle_socket_message, symbol='DOGEUSDT')
twm.start_symbol_ticker_socket(callback=handle_socket_message, symbol='BTCUSDT')

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Отключение WebSocket...")
    twm.stop()


