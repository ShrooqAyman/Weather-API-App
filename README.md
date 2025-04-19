# 🌤️ <a href="https://roadmap.sh/projects/weather-api-wrapper-service">Weather API (Flask + Redis + Rate Limiting)</a>

This is a simple Flask-based Weather API that fetches weather data from the [Visual Crossing Weather API](https://www.visualcrossing.com/), with Redis caching and rate limiting using `flask-limiter`.

---

## 🚀 Features

- Get current and historical weather by location
- Optional date range support (`start_date`, `end_date`)
- Redis-based caching to reduce API calls
- Rate limiting to protect from abuse
- Environment variable support via `.env` file

---

## 📦 Requirements

- Python
- Redis Server
---

## ⚙️ Setup

1. **Clone the repo**

```bash
git clone https://github.com/ShrooqAyman/Weather-API-App.git
cd weather-api
```
2. **Install dependencies**
```bash
   pip install -r requirements.txt
   ```
3. **Run Redis server**
4. **Start the Flask server**
```bash
python app.py
```

## 🔎 API Usage
### GET /weather
Query Parameters:

- location (required): e.g. jerusalem

- start_date (optional): format YYYY-MM-DD

- end_date (optional): format YYYY-MM-DD

### Example:
```bash
/weather?location=jerusalem&start_date=2025-04-01&end_date=2025-04-05
```
