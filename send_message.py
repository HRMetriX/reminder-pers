import os
import requests
from datetime import datetime, timezone

# === Настройка: замени на свой город ===
CITY = "Санкт-Петербург"
LAT = 59.919025  # Широта СПб
LON = 30.304592  # Долгота СПб
# ======================================

# Запрос к Open-Meteo (убраны лишние пробелы!)
weather_url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current_weather=true"
    "&hourly=relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m"
    "&forecast_days=1"
)
weather = requests.get(weather_url).json()

# Базовые данные
temp = weather["current_weather"]["temperature"]
weather_code = weather["current_weather"]["weathercode"]

# Эмодзи погоды
EMOJI_MAP = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌧️", 53: "🌧️", 55: "🌧️",
    61: "🌦️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "🌨️", 75: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}
emoji = EMOJI_MAP.get(weather_code, "🌤️")

# Текущий час в UTC
current_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
try:
    idx = weather["hourly"]["time"].index(current_hour)
except (ValueError, KeyError):
    idx = 0

# Данные
humidity = weather["hourly"]["relative_humidity_2m"][idx]
pressure_hpa = weather["hourly"]["pressure_msl"][idx]  # в гПа
wind_speed_kmh = weather["hourly"]["wind_speed_10m"][idx]  # км/ч
wind_dir_deg = weather["hourly"]["wind_direction_10m"][idx]

# === Перевод давления в мм рт. ст. ===
pressure_mmHg = pressure_hpa * 0.750062

# === Классификация давления ===
if pressure_mmHg < 740:
    pressure_desc = "низкое ⬇️"
elif pressure_mmHg > 770:
    pressure_desc = "высокое ⬆️"
else:
    pressure_desc = "умеренное ↔️"

# === Классификация силы ветра (по шкале Бофорта, упрощённо для км/ч) ===
def wind_strength(speed_kmh):
    if speed_kmh < 5:
        return "слабый"
    elif speed_kmh < 15:
        return "умеренный"
    elif speed_kmh < 25:
        return "сильный"
    elif speed_kmh < 35:
        return "очень сильный"
    else:
        return "буря! 🌪️"

wind_strength_text = wind_strength(wind_speed_kmh)

# === Направление ветра ===
def wind_direction_emoji(deg):
    if 337.5 <= deg or deg < 22.5:
        return "⬆️ С"
    elif 22.5 <= deg < 67.5:
        return "↗️ СВ"
    elif 67.5 <= deg < 112.5:
        return "➡️ В"
    elif 112.5 <= deg < 157.5:
        return "↘️ ЮВ"
    elif 157.5 <= deg < 202.5:
        return "⬇️ Ю"
    elif 202.5 <= deg < 247.5:
        return "↙️ ЮЗ"
    elif 247.5 <= deg < 292.5:
        return "⬅️ З"
    else:
        return "↖️ СЗ"

wind_dir_text = wind_direction_emoji(wind_dir_deg)

# === Формируем сообщение ===
MESSAGE = f"""Здарова, бандиты!

{emoji} Сейчас температура в {CITY} (а именно у подъезда): {temp}°C
💧 Влажность: {humidity:.0f}%
🔽 Давление: {pressure_mmHg:.0f} мм рт.ст. ({pressure_desc})
💨 Ветер: {wind_dir_text}, {wind_speed_kmh:.0f} км/ч — {wind_strength_text}

Не забудь дать ребенку витаминку. ❤️"""

# === Отправка (БЕЗ пробелов в URL!) ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"  # ← исправлено!
response = requests.post(url, json={"chat_id": CHAT_ID, "text": MESSAGE})

if response.status_code == 200:
    print("✅ Сообщение с расширенной погодой отправлено!")
else:
    print("❌ Ошибка:", response.json())
