Win + R → msinfo32
download docker  https://www.docker.com/products/docker-desktop/
Bat/install.bat
adb push X:/ALEX/Python/messenger /storage/sdcard1/
adb push X:\ALEX\Python\messenger\main.py /storage/sdcard1/messenger/main.py
в debain cd /mnt/sdcard1/messenger

войти в Debain /data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/bash

adb shell "su -c '/data/local/linux/bin/bisbox choroot /data/локальный/linux/мnt/тестирование /bin/bash'"
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/bash - запуск linux 
adb push X:\ALEX\Python\messenger\main.py /storage/sdcard1/messenger/ main.py
подопечный компакт-диск /мnt/sdcard1/messenger

клонировать проет на телефон /data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /usr/bin/git clone https://github.com/onesevenrusia-art/Min_messenger.git /root/Min_messenger
обновить /data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /usr/bin/git -C /root/Min_messenger pull
запуск  cd /data/local/linux/mnt/testimg/root/Min_messenger

ИЛИ

adb shell
su
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/bash -c 'cd /root/Min_messenger && /root/venv/bin/python main.py'