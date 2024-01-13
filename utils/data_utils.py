# utils/data_utils.py

# Добавляем функцию для извлечения токена
def extract_token(account_string):
    # Разделяем строку аккаунта по символу ':'
    parts = account_string.split(':')
    # Возвращаем последний элемент, который предполагается токеном
    return parts[-1] if parts else None