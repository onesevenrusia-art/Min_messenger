@echo off
echo 🔄 Сохранение проекта на GitHub...



echo 📦 Добавляем файлы...
git add .

echo 💾 Создаем сохранение...
git commit -m "Auto-save: %date% %time%"

echo 🚀 Отправляем на GitHub...
git push

echo ✅ Проект успешно сохранен на GitHub!
echo 🕐 Время: %date% %time%
pause