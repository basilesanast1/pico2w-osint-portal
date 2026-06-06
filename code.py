import network
import time
import socket
import urequests
import _thread
import ntptime
from machine import Pin

# =========================
# WIFI
# =========================
SSID = "SSID"
PASSWORD = "PASSWORD"

connected = False
ip = "N/A"

headlines = []

# uptime (monotonic)
boot_ms = time.ticks_ms()

# breaking news
previous_headlines = []
breaking_flag = False
breaking_reason = ""

# weather tracking
temperature = "N/A"
weather_desc = "N/A"
last_weather_value = None

RSS_URL = "https://www.theguardian.com/world/rss"

# =========================
# LED
# =========================
led = Pin("LED", Pin.OUT)

def led_pattern(pattern):

    if pattern == "access":
        led.on()
        time.sleep(0.05)
        led.off()

    elif pattern == "new":
        for _ in range(2):
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)

    elif pattern == "breaking":
        for _ in range(6):
            led.on()
            time.sleep(0.05)
            led.off()
            time.sleep(0.05)

    elif pattern == "weather":
        for _ in range(3):
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)

# =========================
# WIFI CONNECT
# =========================
def connect_wifi():
    global connected, ip

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting WiFi...")

    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        connected = True
        ip = wlan.ifconfig()[0]
        print("CONNECTED:", ip)
    else:
        print("WiFi FAILED")

# =========================
# NTP SYNC
# =========================
def sync_time():
    try:
        time.sleep(2)
        ntptime.settime()
        print("NTP synced")
    except:
        print("NTP failed")

# =========================
# UPTIME
# =========================
def get_uptime():
    ms = time.ticks_ms()
    seconds = ms // 1000

    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hrs}h {mins}m {secs}s"

# =========================
# TIME (GREECE UTC+3)
# =========================
def get_time():
    try:
        t = time.localtime(time.time() + 3 * 3600)
        return f"{t[2]:02d}/{t[1]:02d}/{t[0]} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
    except:
        return "TIME ERROR"

# =========================
# CATEGORY SYSTEM
# =========================
def categorize(title):
    t = title.lower()

    if any(x in t for x in ["war", "attack", "military", "russia", "missile", "drone"]):
        return "🔴 GEO-POLITICAL"

    if any(x in t for x in ["economy", "inflation", "market", "trade", "sanctions"]):
        return "💰 ECONOMY"

    if any(x in t for x in ["virus", "ebola", "covid", "health", "outbreak"]):
        return "🟡 HEALTH"

    if any(x in t for x in ["tech", "ai", "software", "apple", "google"]):
        return "🟣 TECH"

    return "⚪ GENERAL"

# =========================
# BREAKING NEWS DETECTOR
# =========================
def detect_breaking(new_list):
    global previous_headlines, breaking_flag, breaking_reason

    new_items = [x for x in new_list if x not in previous_headlines]

    if len(new_items) >= 3:
        breaking_flag = True
        breaking_reason = f"{len(new_items)} new headlines"
        led_pattern("breaking")
    else:
        geo = 0
        health = 0

        for h in new_list[:10]:
            t = h.lower()

            if any(x in t for x in ["war", "attack", "military", "russia", "missile"]):
                geo += 1

            if any(x in t for x in ["virus", "ebola", "covid", "outbreak"]):
                health += 1

        if geo >= 2:
            breaking_flag = True
            breaking_reason = "GEO-POLITICAL SPIKE"
            led_pattern("breaking")

        elif health >= 2:
            breaking_flag = True
            breaking_reason = "HEALTH EMERGENCY SPIKE"
            led_pattern("breaking")

        else:
            breaking_flag = False
            breaking_reason = ""

    previous_headlines = new_list[:]

# =========================
# RSS FETCH
# =========================
def fetch_rss():
    global headlines

    try:
        r = urequests.get(RSS_URL, timeout=10)
        xml = r.text[:30000]
        r.close()

        parts = xml.split("<title>")[1:]
        titles = []

        for p in parts:
            t = p.split("</title>")[0]

            if "World news | The Guardian" in t:
                continue

            t = t.replace("<![CDATA[", "").replace("]]>", "")
            titles.append(t.strip())

        headlines = titles[:20]

        # NEW HEADLINES LED
        if len([x for x in headlines if x not in previous_headlines]) > 0:
            led_pattern("new")

        detect_breaking(headlines)

    except Exception as e:
        print("RSS error:", e)

# =========================
# WEATHER (WITH LED SIGNAL)
# =========================
def fetch_weather():
    global temperature, weather_desc, last_weather_value

    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=39.3625&longitude=22.9425&current_weather=true"

        r = urequests.get(url, timeout=8)
        data = r.json()
        r.close()

        w = data["current_weather"]

        new_temp = w.get("temperature", "N/A")
        wind = w.get("windspeed", "N/A")

        weather_desc = f"Wind {wind} km/h"

        # WEATHER CHANGE DETECTED
        if last_weather_value is not None and new_temp != last_weather_value:
            led_pattern("weather")

        last_weather_value = new_temp
        temperature = new_temp

    except:
        temperature = "N/A"
        weather_desc = "N/A"

# =========================
# WEB PAGE
# =========================
def page():

    now = get_time()
    uptime = get_uptime()

    breaking_html = ""
    if breaking_flag:
        breaking_html = f"""
        <div style="color:red;border:2px solid red;padding:10px;margin:10px 0;">
            🚨 BREAKING NEWS<br>
            {breaking_reason}
        </div>
        """

    news_html = "".join(
        f"<div style='padding:6px;margin-bottom:6px;border-left:2px solid #00ff88'>"
        f"{categorize(h)} | {h}</div>"
        for h in headlines[:10]
    )

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>OSINT DASHBOARD</title>
    </head>

    <body style="background:#0b0b0b;color:#00ff88;font-family:monospace;">

        <h2>[OSINT SYSTEM ACTIVE]</h2>

        {breaking_html}

        <p>[IP]: {ip}</p>
        <p>[TIME]: {now}</p>
        <p>[UPTIME]: {uptime}</p>

        <p>[WEATHER]: {temperature}°C | {weather_desc}</p>

        <p>[ARTICLES]: {len(headlines)}</p>

        <h3>[LATEST HEADLINES]</h3>
        {news_html}

    </body>
    </html>
    """

# =========================
# SERVER
# =========================
def server():
    addr = socket.getaddrinfo("0.0.0.0", 8080)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Server running on 8080")

    while True:
        cl, addr = s.accept()
        try:
            cl.recv(1024)
            led_pattern("access")
            cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n")
            cl.send(page())
        except:
            pass
        finally:
            cl.close()

# =========================
# STARTUP
# =========================
connect_wifi()

while not connected:
    time.sleep(1)

sync_time()

_thread.start_new_thread(server, ())

# =========================
# MAIN LOOP
# =========================
while True:
    fetch_rss()
    time.sleep(3)
    fetch_weather()
    time.sleep(180)