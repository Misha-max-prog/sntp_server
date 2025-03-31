import ntplib
from time import ctime

def main():
    client = ntplib.NTPClient()
    try:
        # Подключаемся к локальному серверу (127.0.0.1:12345)
        # time.windows.com. 127.0.0.1
        response = client.request('127.0.0.1', port=123, version=3)

        print(f"Время, полученное от сервера: {ctime(response.tx_time)}")
    except Exception as e:
        print(f"Ошибка при запросе: {e}")

if __name__ == "__main__":
    main()