# main/app.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from my_vk_api.vk_manager import VKManager
from config.accounts import ACCOUNTS
from config.proxies import PROXIES
from utils.proxy_utils import check_proxy_availability, parse_proxy
import threading
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import queue

# Создание очереди и обработчика для логирования
log_queue = Queue()
queue_handler = QueueHandler(log_queue)
logger = logging.getLogger()
logger.addHandler(queue_handler)
logger.setLevel(logging.INFO)

# Функция для обновления лога в GUI
def update_log_display(log_display, log_queue):
    while True:
        try:
            record = log_queue.get(block=False)
        except queue.Empty:
            break
        else:
            log_display.configure(state='normal')
            log_display.insert(tk.END, f"{record.message}\n")
            log_display.configure(state='disabled')
            log_display.yview(tk.END)

# Функция для копирования текста из лога в буфер обмена
def copy_logs_to_clipboard():
    try:
        text_to_copy = console_log_area.get("1.0", tk.END)
        # Конвертация в строку UTF-8
        text_to_copy = text_to_copy.encode('utf-8').decode('utf-8')
        window.clipboard_clear()
        window.clipboard_append(text_to_copy)
    except Exception as e:
        logger.error(f"Ошибка при копировании логов: {e}")
        tk.messagebox.showerror("Ошибка", f"Не удалось скопировать логи: {e}")

# Функция для очистки текстового поля логов
def clear_console_logs():
    console_log_area.configure(state='normal')
    console_log_area.delete('1.0', tk.END)
    console_log_area.configure(state='disabled')

# Перенос логирования в отдельное текстовое поле
def run_auth():
    vk_manager = VKManager(ACCOUNTS, PROXIES, logger, log_area, window)
    vk_manager.create_sessions(ACCOUNTS, PROXIES)

# Функция для отображения сообщения о загрузке
def show_loading_message(area, message):
    area.insert(tk.END, message + "\n")
    area.update_idletasks()

# Функция для скрытия сообщения о загрузке
def hide_loading_message(area):
    area.delete('1.0', tk.END)

# Функция для блокировки всех кнопок
def disable_buttons():
    test_auth_button.config(state="disabled")
    test_proxy_button.config(state="disabled")
    clear_logs_button.config(state="disabled")
    copy_logs_button.config(state="disabled")

# Функция для разблокировки всех кнопок
def enable_buttons():
    test_auth_button.config(state="normal")
    test_proxy_button.config(state="normal")
    clear_logs_button.config(state="normal")
    copy_logs_button.config(state="normal")

def test_auth():
    def run():
        disable_buttons()
        show_loading_message(log_area, "Загрузка... Проверка авторизации.")
        run_auth()
        hide_loading_message(log_area)
        window.after(0, lambda: hide_loading_message(log_area))
        print("Проверка авторизации завершена.")
        enable_buttons()

    threading.Thread(target=run).start()

# Функция для проверки прокси
def test_proxies():
    def run():
        disable_buttons()
        logger.info("Начало проверки прокси.")
        show_loading_message(proxy_area, "Загрузка... Проверка прокси.")
        working_proxies = 0
        not_working_proxies = 0
        for proxy in PROXIES:
            proxy_dict = parse_proxy(proxy)
            result = check_proxy_availability(proxy_dict)
            if result:
                working_proxies += 1
                logger.info(f"Прокси работает: {proxy_dict}")
            else:
                not_working_proxies += 1
                logger.warning(f"Прокси не работает: {proxy_dict}")
        hide_loading_message(proxy_area)
        proxy_area.insert(tk.END, f"Рабочие прокси: {working_proxies}, Нерабочие прокси: {not_working_proxies}\n")
        window.after(0, lambda: hide_loading_message(proxy_area))
        window.after(0, lambda: proxy_area.insert(tk.END, f"Рабочие прокси: {working_proxies}, Нерабочие прокси: {not_working_proxies}\n"))
        logger.info("Проверка прокси завершена.")
        enable_buttons()

    # Убедимся, что функция запускается только при явном вызове из пользовательского интерфейса
    if "call_from_ui" in threading.current_thread().name:
        threading.Thread(target=run).start()
    
# Создание главного окна
window = tk.Tk()
window.title("VK Manager")
window.geometry("800x600")

# Фрейм для логов авторизации
auth_frame = ttk.LabelFrame(window, text="Логи Авторизации")
auth_frame.place(height=150, width=780, rely=0.05, relx=0.01)

# Создание текстового поля для логов аутентификации
log_area = scrolledtext.ScrolledText(auth_frame, width=94, height=8)
log_area.pack()

# Фрейм для логов прокси
proxy_frame = ttk.LabelFrame(window, text="Логи Прокси")
proxy_frame.place(height=150, width=780, rely=0.35, relx=0.01)

# Создание текстового поля для вывода результатов проверки прокси
proxy_area = scrolledtext.ScrolledText(proxy_frame, width=94, height=8)
proxy_area.pack()

# Фрейм для отображения логов консоли
console_log_frame = ttk.LabelFrame(window, text="Логи Консоли")
console_log_frame.place(height=150, width=780, rely=0.65, relx=0.01)

# Текстовое поле для отображения логов консоли
console_log_area = scrolledtext.ScrolledText(console_log_frame, width=94, height=8)
console_log_area.pack()

# Кнопки управления
button_frame = ttk.Frame(window)
button_frame.place(height=50, width=780, rely=0.90, relx=0.01)

test_auth_button = ttk.Button(button_frame, text="Тестировать авторизацию", command=lambda: threading.Thread(target=test_auth, name="call_from_ui").start())
test_auth_button.pack(side=tk.LEFT, padx=10)

test_proxy_button = ttk.Button(button_frame, text="Проверить прокси", command=lambda: threading.Thread(target=test_proxies, name="call_from_ui").start())
test_proxy_button.pack(side=tk.LEFT, padx=10)

clear_logs_button = ttk.Button(button_frame, text="Очистить Логи Консоли", command=clear_console_logs)
clear_logs_button.pack(side=tk.RIGHT, padx=10)

# Кнопка для копирования логов
copy_logs_button = ttk.Button(button_frame, text="Копировать Логи", command=copy_logs_to_clipboard)
copy_logs_button.pack(side=tk.RIGHT, padx=10)

# Периодическое обновление текстового поля логов
def periodic_log_update():
    update_log_display(console_log_area, log_queue)  # Используйте console_log_area вместо log_display
    window.after(100, periodic_log_update)

# Запуск периодического обновления
window.after(100, periodic_log_update)

# Запуск главного цикла
window.mainloop()