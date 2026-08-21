#!/system/bin/sh

ROOT=/data/local/linux/mnt/testimg
IMG=/storage/sdcard1/debian2g_legacy.img
BUSYBOX=/data/local/linux/bin/busybox

# Создаём loop device
if [ ! -e /dev/loop0 ]; then
    $BUSYBOX mknod /dev/loop0 b 7 0
fi

# Подключаем image
if ! $BUSYBOX losetup -a | $BUSYBOX grep -q "$IMG"; then
    $BUSYBOX losetup /dev/loop0 "$IMG"
fi

# Создаём mount point
$BUSYBOX mkdir -p "$ROOT"

# Монтируем Debian
if ! $BUSYBOX mount | $BUSYBOX grep -q "on $ROOT type ext4"; then
    $BUSYBOX mount -t ext4 /dev/loop0 "$ROOT"
fi

# /proc
if ! $BUSYBOX mount | $BUSYBOX grep -q "on $ROOT/proc "; then
    $BUSYBOX mount -t proc proc "$ROOT/proc"
fi

# /sys
if ! $BUSYBOX mount | $BUSYBOX grep -q "on $ROOT/sys "; then
    $BUSYBOX mount -t sysfs sysfs "$ROOT/sys"
fi

# /dev
if ! $BUSYBOX mount | $BUSYBOX grep -q "on $ROOT/dev "; then
    $BUSYBOX mount --bind /dev "$ROOT/dev"
fi

# /dev/pts
$BUSYBOX mkdir -p "$ROOT/dev/pts"

if ! $BUSYBOX mount | $BUSYBOX grep -q "on $ROOT/dev/pts "; then
    $BUSYBOX mount -t devpts devpts "$ROOT/dev/pts"
fi

# Debian environment
export HOME=/root
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export SHELL=/bin/bash
export TERM=vt100

# Запуск Debian
exec $BUSYBOX chroot "$ROOT" /bin/bash --login