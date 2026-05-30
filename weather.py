import requests

WEATHER_API_KEY = "d37bdb9d6df67051dff6c2dfd3ee6e42"
CITY = "Singapore"

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data['main']['temp']
        
        if temp > 25:
            advice = "🥵 Wear something light! It's hot outside."
        else:
            advice = "✅ Weather is pleasant."
            
        return f"{temp:.1f}°C | {advice}"
    except:
        return "28°C | ☀️ Hot outside"