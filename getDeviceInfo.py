import os

def get_battery():
    base = "/sys/class/power_supply"

    try:
        for name in os.listdir(base):
            path = os.path.join(base, name)

            cap = os.path.join(path, "capacity")
            if os.path.exists(cap):
                with open(cap) as f:
                    percent = f.read().strip()

                status = "unknown"
                status_file = os.path.join(path, "status")

                if os.path.exists(status_file):
                    with open(status_file) as f:
                        status = f.read().strip()

                return {
                    "percent": percent,
                    "status": status
                }
    except Exception:
        pass

    return None

import os

def get_log(lines=50):
    try:
        with open("server.log", "r", encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-lines:])
    except Exception as e:
        return str(e)

def get_ram():
    data = {}

    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":", 1)

            if key in ("MemTotal", "MemFree", "Buffers", "Cached"):
                data[key] = int(value.split()[0]) * 1024

    total = data["MemTotal"]
    free = data["MemFree"]
    buffers = data.get("Buffers", 0)
    cached = data.get("Cached", 0)

    return {
        "total": total,
        "free": free,
        "used": total - free - buffers - cached
    }

def get_disk(path):
    s = os.statvfs(path)

    total = s.f_blocks * s.f_frsize
    free = s.f_bavail * s.f_frsize
    used = total - free

    return {
        "total": total,
        "used": used,
        "free": free
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