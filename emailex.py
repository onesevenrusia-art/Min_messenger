import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# 1. Конфигурация
email_from = 'onesevenrusia@gmail.com'  # Ваш Gmail-адрес
password = 'qhxw zqci vqit xwvp'  # Ваш пароль ПРИЛОЖЕНИЯ, сгенерированный для Python
email_to = 'olegpobrey@gmail.com'  # Email получателя (кому отправляем код)

# 2. Генерация случайного 6-значного кода
verification_code = str(random.randint(100000, 999999))

# 3. Формирование сообщения
msg = MIMEMultipart()
msg['From'] = email_from
msg['To'] = email_to
msg['Subject'] = 'Ваш код подтверждения'

# Текст сообщения (можно оформить и в HTML)
body = f"""
Здравствуйте!
Ваш код для подтверждения: <b>{verification_code}</b>

Никому не сообщайте этот код.
"""
msg.attach(MIMEText(body, 'html'))  # Используйте 'plain' для обычного текста

# 4. Отправка сообщения через SMTP-сервер Gmail
try:
    # Создаем соединение с SMTP-сервером Gmail (порт 587 для TLS)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Шифруем соединение
    server.login(email_from, password)  # Логинимся на сервер
    text = msg.as_string()  # Преобразуем сообщение в строку
    server.sendmail(email_from, email_to, text)  # Отправляем письмо
    print('Код успешно отправлен!')
    print(f'Сгенерированный код: {verification_code}') # Для отладки, в реальном приложении не выводите код

except Exception as e:
    print(f'Произошла ошибка при отправке: {e}')

finally:
    server.quit()  # Всегда закрываем соединение


def SendCode(emailreciver):
    email_from = 'onesevenrusia@gmail.com' 
    password = 'qhxw zqci vqit xwvp'  
    email_to = emailreciver
    code=str(random.randint(100000, 999999))
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = 'Ваш код подтверждения'
    body = f"""
    Здравствуйте!
    Ваш код для подтверждения: <b>{code}</b>

    Никому не сообщайте этот код.
    """
    msg.attach(MIMEText(body, 'html')) 
    try:
        # Создаем соединение с SMTP-сервером Gmail (порт 587 для TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Шифруем соединение
        server.login(email_from, password)  # Логинимся на сервер
        text = msg.as_string()  # Преобразуем сообщение в строку
        server.sendmail(email_from, email_to, text)  # Отправляем письмо
    except Exception as e:
        print(f'Произошла ошибка при отправке: {e}')
        return e
    finally:
        server.quit()
        return [True, code]