# utils/proxy_utils.py
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_proxy_availability(proxy_dict):
    try:
        response = requests.get("http://www.google.com", proxies=proxy_dict, timeout=5)
        if response.status_code == 200:
            logger.info(f"Прокси работает: {proxy_dict}")
            return True
        else:
            logger.warning(f"Прокси не работает с кодом ошибки {response.status_code}: {proxy_dict}")
            return False
    except requests.RequestException as e:
        logger.error(f"Ошибка проверки прокси {e}: {proxy_dict}")
        return False

def parse_proxy(proxy_string):
    # Разделяем строку прокси на части
    user_password, host_port = proxy_string.split('@')
    user, password = user_password.split(':')
    host, port = host_port.split(':')

    # Используем HTTP вместо HTTPS
    return {
        'http': f'http://{user}:{password}@{host}:{port}',
        'https': f'http://{user}:{password}@{host}:{port}'  # Замените https на http
    }

