@echo off
echo 📥 Загрузка файлов из GitHub...


echo 🔄 Получаем последние изменения...
git fetch origin

echo 📋 Заменяем файлы на версию из GitHub...
git reset --hard origin/main

echo ✅ Файлы успешно заменены на версию из GitHub!
echo 🕐 Время: %date% %time%
pause