
import os
import subprocess


def get_battery():
    # 1. Linux /sys/class/power_supply
    base = "/sys/class/power_supply"

    try:
        if os.path.isdir(base):
            for name in os.listdir(base):
                path = os.path.join(base, name)

                capacity = os.path.join(path, "capacity")
                status = os.path.join(path, "status")

                if os.path.isfile(capacity):
                    with open(capacity, "r") as f:
                        percent = f.read().strip()

                    state = "unknown"

                    if os.path.isfile(status):
                        with open(status, "r") as f:
                            state = f.read().strip()

                    return {
                        "percent": percent,
                        "status": state
                    }
    except Exception:
        pass

    # 2. Android dumpsys battery
    try:
        result = subprocess.run(
            ["dumpsys", "battery"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            percent = "?"
            status = "unknown"

            for line in result.stdout.splitlines():
                line = line.strip()

                if line.startswith("level:"):
                    percent = line.split(":", 1)[1].strip()

                elif line.startswith("status:"):
                    value = line.split(":", 1)[1].strip()

                    statuses = {
                        "1": "unknown",
                        "2": "charging",
                        "3": "discharging",
                        "4": "not charging",
                        "5": "full"
                    }

                    status = statuses.get(value, value)

            return {
                "percent": percent,
                "status": status
            }

    except Exception:
        pass

    # 3. Ничего не удалось получить
    return {
        "percent": "?",
        "status": "unavailable"
    }


def get_log(lines=50):
    try:
        with open(
            "server.log",
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:
            return "".join(f.readlines()[-lines:])

    except Exception as e:
        return str(e)


def get_ram():
    data = {}

    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                key, value = line.split(":", 1)

                if key in (
                    "MemTotal",
                    "MemFree",
                    "MemAvailable",
                    "Buffers",
                    "Cached"
                ):
                    data[key] = int(value.split()[0]) * 1024

    except Exception:
        return {
            "total": 0,
            "free": 0,
            "used": 0
        }

    total = data.get("MemTotal", 0)

    # MemAvailable значительно полезнее MemFree
    # для отображения реально доступной памяти.
    if "MemAvailable" in data:
        free = data["MemAvailable"]
    else:
        free = (
            data.get("MemFree", 0)
            + data.get("Buffers", 0)
            + data.get("Cached", 0)
        )

    used = max(0, total - free)

    return {
        "total": total,
        "free": free,
        "used": used
    }


def get_disk(path="."):
    try:
        s = os.statvfs(path)

        total = s.f_blocks * s.f_frsize
        free = s.f_bavail * s.f_frsize
        used = total - free

        return {
            "total": total,
            "used": used,
            "free": free
        }

    except Exception:
        return {
            "total": 0,
            "used": 0,
            "free": 0
        }

def mb(value):
    return round(value / 1024 / 1024, 1)

def gb(value):
    return round(value / 1024 / 1024 / 1024, 2)

def get_dev_page():

    ram = get_ram()
    battery = get_battery()
    internal = get_disk("/")
    log = get_log(50)

    try:
        sd = get_disk("/storage/sdcard1")
        sd_html = f"""
        <p>
            Total: {gb(sd["total"])} GB<br>
            Used: {gb(sd["used"])} GB<br>
            Free: {gb(sd["free"])} GB
        </p>
        """
    except Exception as e:
        sd_html = f"<p>SD: {e}</p>"

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<meta http-equiv="refresh" content="5">

<title>Server DEV</title>

<style>

body {{
    background:#111;
    color:#ddd;
    font-family:monospace;
    margin:30px;
}}

.card {{
    background:#1c1c1c;
    padding:15px;
    margin-bottom:15px;
    border-radius:8px;
}}

h1 {{
    color:#fff;
}}

pre {{
    background:#000;
    padding:15px;
    overflow:auto;
    max-height:400px;
}}

.ok {{
    color:#5f5;
}}

</style>
</head>

<body>

<h1>Server DEV</h1>

<div class="card">
<h2>RAM</h2>

Total: {mb(ram["total"])} MB<br>
Used: {mb(ram["used"])} MB<br>
Free: <span class="ok">{mb(ram["free"])} MB</span>

</div>

<div class="card">

<h2>Battery</h2>

Charge: <b>{battery.get("percent", "?")}%</b><br>
Status: {battery.get("status", "?")}

</div>

<div class="card">

<h2>Internal storage</h2>

Total: {gb(internal["total"])} GB<br>
Used: {gb(internal["used"])} GB<br>
Free: {gb(internal["free"])} GB

</div>

<div class="card">

<h2>SD card</h2>

{sd_html}

</div>

<div class="card">

<h2>server.log</h2>

<pre>{log}</pre>

</div>

</body>
</html>
"""