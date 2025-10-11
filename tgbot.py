from flask import Flask, request, jsonify
import telebot
import hashlib
import hmac
import time

app = Flask(__name__)
# Ваш секретный ключ от BotFather
TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

def verify_telegram_data(init_data_str):
    """
    Проверяет, что данные от Telegram подлинные.
    Это КРИТИЧЕСКИ важный шаг для безопасности.
    """
    try:
        # Парсим данные
        data_pairs = init_data_str.split('&')
        data_dict = {}
        for pair in data_pairs:
            key, value = pair.split('=')
            data_dict[key] = value

        # Извлекаем хэш и сами данные
        received_hash = data_dict.get('hash', '')
        auth_date = data_dict.get('auth_date', '')

        # Проверяем свежесть данных (не старше 24 часов)
        if time.time() - int(auth_date) > 86400:
            return False, "Data is too old"

        # Убираем хэш из данных для проверки
        data_check_string = '\n'.join([f"{k}={data_dict[k]}" for k in sorted(data_dict.keys()) if k != 'hash'])

        # Создаем секретный ключ
        secret_key = hmac.new("WebAppData".encode(), TOKEN.encode(), hashlib.sha256).digest()
        # Вычисляем свой хэш
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Сравниваем хэши
        if computed_hash == received_hash:
            return True, data_dict
        else:
            return False, "Invalid hash"

    except Exception as e:
        return False, f"Error: {str(e)}"

@app.route('/api/auth/telegram', methods=['POST'])
def auth_telegram():
    init_data = request.json.get('auth_data')
    is_valid, result = verify_telegram_data(init_data)

    if not is_valid:
        return jsonify({'success': False, 'error': result}), 401

    # Данные подлинные! Извлекаем информацию о пользователе
    user_data = result
    user_id = user_data.get('id')
    first_name = user_data.get('first_name')
    username = user_data.get('username')

    # Здесь вы:
    # 1. Находите или создаете пользователя в своей БД по user_id
    # 2. Генерируете JWT-токен или сессию для этого пользователя
    # 3. Возвращаете токен клиенту

    # Пример (упрощенно):
    # user = find_or_create_user(user_id, first_name, username)
    # auth_token = generate_jwt_token(user_id)

    return jsonify({
        'success': True,
        'user': {
            'id': user_id,
            'first_name': first_name,
            'username': username
        },
        'token': 'your_generated_jwt_token_here' # Верните сгенерированный токен
    })

if __name__ == '__main__':
    app.run(ssl_context='adhoc') # HTTPS важен для Telegram Web App!