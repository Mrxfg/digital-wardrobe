# Weather API Integration Guide

## Overview

The Digital Wardrobe now includes weather information to help users choose appropriate outfits based on current and forecasted weather conditions.

## API Provider

**OpenWeatherMap** (Free Tier)
- 1000 API calls per day
- Perfect for ~1000 users (each checking weather once per day)
- Current weather + 5-day forecast
- Global coverage

## Setup

### 1. Get API Key (FREE)

1. Go to https://openweathermap.org/api
2. Click "Sign Up" (free account)
3. Verify your email
4. Go to API Keys section
5. Copy your API key

### 2. Add to .env file

```env
OPENWEATHER_API_KEY=your-api-key-here
```

### 3. Restart your server

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Get Current Weather

**Endpoint:** `GET /weather/current`

**Parameters:**
- `city` (required): City name (e.g., "Tashkent", "New York")
- `country` (optional): ISO 3166 country code (e.g., "UZ", "US")

**Example Request:**
```bash
curl "http://localhost:8000/weather/current?city=Tashkent&country=UZ"
```

**Example Response:**
```json
{
  "temperature": 32.5,
  "feels_like": 35.2,
  "temp_min": 30.0,
  "temp_max": 34.0,
  "humidity": 45,
  "description": "clear sky",
  "condition": "Clear",
  "icon": "01d",
  "wind_speed": 3.5,
  "city": "Tashkent",
  "country": "UZ"
}
```

### Get Weather Forecast

**Endpoint:** `GET /weather/forecast`

**Parameters:**
- `city` (required): City name
- `country` (optional): ISO 3166 country code
- `days` (optional): Number of days (1-5, default: 3)

**Example Request:**
```bash
curl "http://localhost:8000/weather/forecast?city=Tashkent&country=UZ&days=3"
```

**Example Response:**
```json
{
  "city": "Tashkent",
  "country": "UZ",
  "forecasts": [
    {
      "datetime": "2026-06-18 15:00:00",
      "temperature": 32.5,
      "feels_like": 35.2,
      "temp_min": 30.0,
      "temp_max": 34.0,
      "description": "clear sky",
      "condition": "Clear",
      "icon": "01d",
      "humidity": 45,
      "wind_speed": 3.5
    },
    // ... more 3-hour forecasts
  ]
}
```

## Weather Icons

OpenWeatherMap provides icon codes (e.g., "01d", "10n") that you can display:

**Icon URL format:**
```
https://openweathermap.org/img/wn/{icon}@2x.png
```

**Example:**
```html
<img src="https://openweathermap.org/img/wn/01d@2x.png" alt="weather icon">
```

## Weather Conditions

Common condition values:
- `Clear` - Clear sky
- `Clouds` - Cloudy
- `Rain` - Rainy
- `Snow` - Snowy
- `Thunderstorm` - Stormy
- `Drizzle` - Light rain
- `Mist` / `Fog` - Misty/Foggy

## Usage Examples

### Outfit Recommendations Based on Weather

```javascript
// Get current weather
const weather = await fetch('/weather/current?city=Tashkent&country=UZ');
const data = await weather.json();

// Recommend clothes based on temperature
if (data.temperature < 10) {
  console.log("Wear warm clothes: jacket, sweater");
} else if (data.temperature < 20) {
  console.log("Wear light jacket or cardigan");
} else {
  console.log("Wear light summer clothes");
}

// Check for rain
if (data.condition === "Rain") {
  console.log("Don't forget umbrella and raincoat!");
}
```

### Telegram Mini App Integration

```javascript
// In your Telegram Mini App
async function getWeatherAndSuggestOutfit() {
  // Get user's location from Telegram
  const location = window.Telegram.WebApp.initData.location;
  
  // Fetch weather
  const response = await fetch(
    `${API_URL}/weather/current?city=${location.city}`
  );
  const weather = await response.json();
  
  // Show weather card
  showWeatherCard(weather);
  
  // Filter clothes by season/weather
  const suitableClothes = await fetch(
    `${API_URL}/clothes?season=${getSeason(weather.temperature)}`
  );
}
```

## Rate Limits

**Free Tier Limits:**
- 1000 calls/day
- 60 calls/minute

**Tips for staying within limits:**
1. Cache weather data for 30-60 minutes
2. Only fetch when user explicitly requests
3. Use forecast endpoint for planning (fewer calls)

## Error Handling

**City not found:**
```json
{
  "error": "City not found"
}
```

**API key not configured:**
```json
{
  "error": "Weather API key not configured"
}
```

**API timeout:**
```json
{
  "error": "Weather API timeout"
}
```

## Caching (Recommended)

To reduce API calls, implement caching:

```python
# Add to your .env
WEATHER_CACHE_MINUTES=30

# Weather updates every 30 minutes is enough
# This reduces 1000 daily calls to ~48 calls per user per day
```

## Testing

Test the endpoints in your browser or with curl:

```bash
# Test current weather
curl "http://localhost:8000/weather/current?city=Tashkent"

# Test forecast
curl "http://localhost:8000/weather/forecast?city=Tashkent&days=5"

# Test with country code
curl "http://localhost:8000/weather/current?city=New York&country=US"
```

## Interactive API Docs

Visit: `http://localhost:8000/docs`

You can test all weather endpoints directly in the browser!

## Upgrade Options (If Needed)

If you exceed 1000 calls/day, consider:

1. **Implement caching** (recommended first)
2. **Upgrade OpenWeatherMap** ($40/month for 100K calls)
3. **Switch to WeatherAPI.com** (1M free calls/month)

For 1000 users, free tier should be sufficient with basic caching! 🌤️
