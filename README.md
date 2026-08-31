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
ИЛИ
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/bash -c 'cd /root/Min_messenger && /root/venv/bin/python main.py'

Найти ID процесса
ps | grep python
kill номер процесса для остановки
______________
баги с wifi
1|root@android:/ # settings get global wifi_sleep_policy
3
root@android:/ # settings put global wifi_sleep_policy 2
root@android:/ # settings get global wifi_sleep_policy
2
тест с windows    Test-NetConnection 192.168.1.33 -Port 443
______________

запуск намертво с поддержкой отключения adb
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/bash -c 'cd /root/Min_messenger && /root/venv/bin/python main.py >server.log 2>&1 &'
проверка
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/ps
/data/local/linux/bin/busybox netstat -lnpt | grep :443
Логи
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /bin/cat /root/Min_messenger/server.log


Для состояния Wi-Fi на Android лучше всего:
    /data/local/linux/bin/busybox ip addr show wlan0
wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>

getprop dhcp.wlan0.result
    ok

обновить с git актуально
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /usr/bin/git -C /root/Min_messenger reset --hard
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /usr/bin/git -C /root/Min_messenger clean -fd
/data/local/linux/bin/busybox chroot /data/local/linux/mnt/testimg /usr/bin/git -C /root/Min_messenger pull

список работающиз сервисов ps > /sdcard/ps_before.txt

stop servises
am force-stop com.mgyapp.android
am force-stop com.android.chrome
am force-stop com.google.android.youtube
am force-stop com.google.android.apps.plus
am force-stop com.google.android.apps.uploader
am force-stop com.lenovo.email
am force-stop com.lenovo.exchange
am force-stop com.lenovo.videoplayer
am force-stop com.lenovo.app.Calendar
pm disable com.android.chrome
pm disable com.android.browser
pm disable com.android.calculator2
pm disable com.google.android.apps.books
pm disable com.google.android.apps.genie.geniewidget
pm disable com.google.android.apps.magazines
pm disable com.google.android.apps.maps
pm disable com.google.android.apps.plus
pm disable com.google.android.apps.uploader
pm disable com.google.android.gm
pm disable com.google.android.googlequicksearchbox
pm disable com.google.android.music
pm disable com.google.android.play.games
pm disable com.google.android.street
pm disable com.google.android.talk
pm disable com.google.android.videos
pm disable com.google.android.youtube
pm disable com.google.android.voicesearch
pm disable com.lenovo.BackupRestore
pm disable com.lenovo.FileBrowser
pm disable com.lenovo.MobileLog
pm disable com.lenovo.app.Calendar
pm disable com.lenovo.compass
pm disable com.lenovo.deskclock
pm disable com.lenovo.email
pm disable com.lenovo.exchange
pm disable com.lenovo.facebook
pm disable com.lenovo.ideafriend
pm disable com.lenovo.ideawallpaper
pm disable com.lenovo.launcher
pm disable com.lenovo.launcher.theme.a789_1
pm disable com.lenovo.launcher.theme.a789_2
pm disable com.lenovo.launcher.theme.a789_3
pm disable com.lenovo.launcher.theme.a789_4
pm disable com.lenovo.launcher.theme.theme1
pm disable com.lenovo.ota
pm disable com.lenovo.scg
pm disable com.lenovo.videoplayer

pm disable com.android.dreams.basic
pm disable com.android.dreams.phototable
pm disable com.android.galaxy4
pm disable com.android.magicsmoke
pm disable com.android.noisefield
pm disable com.android.phasebeam
pm disable com.android.wallpaper
pm disable com.android.wallpaper.holospiral
pm disable com.android.wallpaper.livepicker

pm disable com.android.soundrecorder
pm disable com.android.musicfx
pm disable com.android.musicvis
pm disable com.mediatek.videofavorites
pm disable com.mediatek.vlw
pm disable com.mediatek.voicecommand
pm disable com.mediatek.voiceunlock
pm disable com.mediatek.ygps

pm disable com.mgyapp.android

остановленные приложения pm list packages -d