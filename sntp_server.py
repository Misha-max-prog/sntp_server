import socket
import struct
import time

# чтение config.txt
def read_config():
    with open('config.txt', 'r') as file:
        line = file.readline().strip()
        key, value = line.split("=")
        return int(value.strip())

# получение NTP-времени с учетом сдвига
# NTP-формат
def get_ntp_time(time_shift=0):
    unix_time = time.time() + time_shift  # Текущее UNIX-время с учетом сдвига
    ntp_time = unix_time + 2208988800  # Конвертация в NTP-время
    seconds = int(ntp_time)  # Целая часть секунд
    fraction = int((ntp_time - seconds) * (2**32))  # Доли секунды
    return seconds, fraction

# ответ SNTP-сервера
def create_sntp_response(originate_timestamp, receive_time, transmit_time):
    response = bytearray(48)  # Создаем массив байтов длиной 48
    response[0] = 0x1C  # Поле LI, Версия, Режим (Server)
    response[1] = 1      # Stratum = 1 (Первичный сервер)
    response[2] = 0      # Интервл опроса (Poll interval)
    response[3] = 0      # Точность (Precision)

    # Root Delay и Root Dispersion (заполняем нулями)
    response[4:8] = b'\0\0\0\0'
    response[8:12] = b'\0\0\0\0'

    # Идентификатор источника времени (Reference Identifier)
    response[12:16] = b'LOCL'  # Указываем локальное время

    # Записываем временные метки в ответ
    response[16:24] = struct.pack('!II', *receive_time)  # Время ссылки (Reference Timestamp)
    response[24:32] = originate_timestamp  # Время отпраки клиентом (Originate Timestamp)
    response[32:40] = struct.pack('!II', *receive_time)  # Время получения запроса (Receive Timestamp)
    response[40:48] = struct.pack('!II', *transmit_time)  # Время отправки ответа (Transmit Timestamp)

    return response

# запуск SNTP-сервера
def start_sntp_server():
    time_shift = read_config()  # Читаем сдвиг времени из конфигурационного файла
    print(f"Сервер запущен. Сдвиг времени из конфига: {time_shift} секунд")

    server_address = ('127.0.0.1', 123)  # Запускаем сервер на локальном хосте и порту 123
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Создаем UDP-сокет
    sock.bind(server_address)  # Привязываем его к адресу и порту
    print(f"Слушаем на {server_address}")

    while True:
        data, address = sock.recvfrom(1024)  # Получаем запрос от клиента
        print(f"Получен запрос от {address}")

        # Извлекаем Originate Timestamp (время отправки клиентом)
        originate_timestamp = data[40:48]

        # Время получения запроса (без сдвига)
        receive_time = get_ntp_time()

        # Время отправки ответа (с учетом сдвига)
        transmit_time = get_ntp_time(time_shift)

        # Создаем ответный SNTP-пакет
        response = create_sntp_response(originate_timestamp, receive_time, transmit_time)

        # Преобразуем передаваемое время в читаемый формат
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(transmit_time[0]))
        print(f"Отправляем клиенту время: {readable_time} (сдвиг: {time_shift} секунд)")

        # Отправляем ответ клиенту
        sock.sendto(response, address)

# Запуск сервера
if __name__ == '__main__':
    start_sntp_server()
