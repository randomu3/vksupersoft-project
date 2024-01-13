# my_vk_api/vk_manager.py
import logging
import requests
import vk_api
from utils.proxy_utils import check_proxy_availability, parse_proxy
from utils.data_utils import extract_token
import tkinter as tk

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VKManager:
    def __init__(self, accounts, proxies, logger, log_area, window):
        self.window = window
        self.logger = logger
        self.log_area = log_area  # Сохраняем ссылку на текстовое поле
        self.success_count = 0
        self.failure_count = 0
        self.sessions = self.create_sessions(accounts, proxies)

    def print_summary(self):
        summary_message = f"Итог: {self.success_count} успешных, {self.failure_count} неудачных авторизаций"
        # Очищаем log_area перед выводом итогов
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.insert(tk.END, summary_message + "\n")
        self.log_area.configure(state='disabled')

    def create_sessions(self, accounts, proxies):
        self.success_count = 0  # Обнуляем счетчики перед началом создания сессий
        self.failure_count = 0
        sessions = []  # Инициализация списка сессий

        for account, proxy in zip(accounts, proxies):
            logger.info(f"Настройка сессии для аккаунта: {account}")
            token = extract_token(account)
            proxy_dict = parse_proxy(proxy)

            if not check_proxy_availability(proxy_dict):
                logger.warning(f"Проверка прокси не удалась для аккаунта: {account}")
                successful_auth = False
            else:
                api_response = requests.get(
                    'https://api.vk.com/method/users.get',
                    params={'access_token': token, 'v': '5.92'},
                    proxies=proxy_dict
                )
                if api_response.status_code == 200 and api_response.json().get('response'):
                    session = {'token': token, 'proxy': proxy_dict}
                    sessions.append(session)
                    successful_auth = True
                else:
                    successful_auth = False

            if successful_auth:
                self.success_count += 1
            else:
                self.failure_count += 1

        self.window.after(0, self.print_summary)
        return sessions
