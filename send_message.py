import os
import requests
from datetime import datetime, timezone

# === Настройка: замени на свой город ===
CITY = "Санкт-Петербург"
LAT = 59.919025  # Широта СПб
LON = 30.304592  # Долгота СПб
# ======================================

# Запрос к Open-Meteo с расширенными данными
weather_url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current_weather=true"
    "&hourly=relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m"
    "&forecast_days=1"
)
weather = requests.get(weather_url).json()

# Базовые данные из current_weather
temp = weather["current_weather"]["temperature"]
weather_code = weather["current_weather"]["weathercode"]

# Эмодзи по погоде
EMOJI_MAP = {
    0: "☀️",   # Clear sky
    1: "🌤️",   # Mainly clear
    2: "⛅",   # Partly cloudy
    3: "☁️",   # Overcast
    45: "🌫️",  # Fog
    48: "🌫️",  # Depositing rime fog
    51: "🌧️",  # Drizzle: Light
    53: "🌧️",  # Drizzle: Moderate
    55: "🌧️",  # Drizzle: Dense
    61: "🌦️",  # Rain: Slight
    63: "🌧️",  # Rain: Moderate
    65: "🌧️",  # Rain: Heavy
    71: "❄️",  # Snow: Slight
    73: "🌨️",  # Snow: Moderate
    75: "🌨️",  # Snow: Heavy
    95: "⛈️",  # Thunderstorm
    96: "⛈️",  # Thunderstorm with hail
    99: "⛈️",  # Thunderstorm with hail
}
emoji = EMOJI_MAP.get(weather_code, "🌤️")

# Определяем текущий час в UTC для выбора hourly-данных
current_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
try:
    idx = weather["hourly"]["time"].index(current_hour)
except (ValueError, KeyError):
    idx = 0  # fallback на первый доступный час

# Извлекаем расширенные параметры
humidity = weather["hourly"]["relative_humidity_2m"][idx]
pressure = weather["hourly"]["pressure_msl"][idx]  # в гПа
wind_speed = weather["hourly"]["wind_speed_10m"][idx]  # км/ч
wind_dir = weather["hourly"]["wind_direction_10m"][idx]  # градусы

# Определяем направление ветра (с эмодзи)
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

wind_text = f"{wind_direction_emoji(wind_dir)} {wind_speed:.0f} км/ч"

# Формируем сообщение — в твоём стиле, но с доп. данными
MESSAGE = f"""Здарова, бандиты!

{emoji} Сейчас температура в {CITY} (а именно у подъезда): {temp}°C
💧 Влажность: {humidity:.0f}%
🔽 Давление: {pressure:.0f} гПа
💨 Ветер: {wind_text}

Не забудь дать ребенку витаминку. ❤️"""


# === Отправка через Telegram ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
response = requests.post(url, json={"chat_id": CHAT_ID, "text": MESSAGE})

if response.status_code == 200:
    print("✅ Сообщение с полной погодой отправлено!")
else:
    print("❌ Ошибка:", response.json())
