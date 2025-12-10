import os
import requests
from datetime import datetime, timezone

# === Настройка: замени на свой город ===
CITY = "Санкт-Петербург"
LAT = 59.919025
LON = 30.304592
# ======================================

# Запрос к Open-Meteo (без лишних пробелов!)
weather_url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    f"&current_weather=true"
    f"&hourly=relative_humidity_2m,pressure_msl,"
    f"apparent_temperature,precipitation,cloudcover,visibility"
    f"&forecast_days=1"
)

weather = requests.get(weather_url).json()

# === Текущие данные ===
temp = weather["current_weather"]["temperature"]
weather_code = weather["current_weather"]["weathercode"]
wind_speed_kmh = weather["current_weather"]["windspeed"]      # из current!
wind_dir_deg = weather["current_weather"]["winddirection"]    # из current!
is_day = bool(weather["current_weather"]["is_day"])

# === Определение текущего часа в UTC для hourly-данных ===
current_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
try:
    idx = weather["hourly"]["time"].index(current_hour)
except (ValueError, KeyError):
    idx = 0  # fallback на первый час

# === Hourly-параметры ===
humidity = weather["hourly"]["relative_humidity_2m"][idx]
pressure_hpa = weather["hourly"]["pressure_msl"][idx]
apparent_temp = weather["hourly"]["apparent_temperature"][idx]
precipitation = weather["hourly"]["precipitation"][idx]
cloudcover = weather["hourly"]["cloudcover"][idx]
visibility_m = weather["hourly"]["visibility"][idx]  # в метрах

# === Перевод давления в мм рт. ст. ===
pressure_mmHg = pressure_hpa * 0.750062

# === Эмодзи погоды (WMO) ===
EMOJI_MAP = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌧️", 53: "🌧️", 55: "🌧️",
    61: "🌦️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "🌨️", 75: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}
emoji = EMOJI_MAP.get(weather_code, "🌤️")

# === Интерпретация: Ощущаемая температура ===
def temp_feel(ap_temp):
    if ap_temp < -15:
        return "морозище ❄️"
    elif ap_temp < -5:
        return "очень холодно 🥶"
    elif ap_temp < 0:
        return "холодно 🧣"
    elif ap_temp < 10:
        return "прохладно 🧥"
    elif ap_temp < 20:
        return "комфортно 👌"
    elif ap_temp < 25:
        return "тепло ☀️"
    elif ap_temp < 30:
        return "жарко 🌞"
    else:
        return "палящий зной 🔥"

feel_desc = temp_feel(apparent_temp)

# === Интерпретация: Осадки ===
def precip_desc(precip):
    if precip <= 0.0:
        return "без дождя 🌤️"
    elif precip < 0.5:
        return "морось 💧"
    elif precip < 2.0:
        return "дождь 🌧️"
    elif precip < 10.0:
        return "сильный дождь 🌧️🌧️"
    else:
        return "ливень! 🌊"

precip_text = precip_desc(precipitation)

# === Интерпретация: Облачность ===
def cloud_desc(cover):
    if cover < 20:
        return "ясно"
    elif cover < 60:
        return "переменная облачность"
    else:
        return "пасмурно"

cloud_text = cloud_desc(cloudcover)

# === Интерпретация: Давление ===
if pressure_mmHg < 740:
    pressure_desc = "низкое ⬇️"
elif pressure_mmHg > 770:
    pressure_desc = "высокое ⬆️"
else:
    pressure_desc = "умеренное ↔️"

# === Интерпретация: Сила ветра (шкала Бофорта, упрощённо) ===
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

# === Видимость (в км) ===
visibility_km = visibility_m / 1000
if visibility_km < 1:
    visibility_text = f"{visibility_km:.1f} км — туман/снегопад! 🌫️"
elif visibility_km < 5:
    visibility_text = f"{visibility_km:.0f} км — ограничена"
elif visibility_km < 10:
    visibility_text = f"{visibility_km:.0f} км — нормальная"
else:
    visibility_text = f"{visibility_km:.0f} км — отличная 👀"

# === Формируем сообщение ===
MESSAGE = f"""Здарова, бандиты!

{emoji} Сейчас в {CITY} (а именно у подъезда):
🌡️ {temp:.1f}°C {'(ночь 🌙)' if not is_day else '(день ☀️)'}
    ощущается как {apparent_temp:.1f}°C — {feel_desc}
💧 Влажность: {humidity:.0f}%
☁️ Облачность: {cloud_text} ({cloudcover:.0f}%)
{precipitation > 0.1 and '🌧️ ' or ''}Осадки: {precip_text} ({precipitation:.1f} мм/ч)
🔽 Давление: {pressure_mmHg:.0f} мм рт.ст. ({pressure_desc})
💨 Ветер: {wind_dir_text}, {wind_speed_kmh:.1f} км/ч — {wind_strength_text}
👁️ Видимость: {visibility_text}

Не забудь дать ребенку витаминку. ❤️"""

# === Отправка (БЕЗ пробелов в URL!) ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"  # ← исправлено!
response = requests.post(url, json={"chat_id": CHAT_ID, "text": MESSAGE})

if response.status_code == 200:
    print("✅ Сообщение с расширенной погодой отправлено!")
    print(MESSAGE)
else:
    print("❌ Ошибка:", response.json())
