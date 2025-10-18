# Quick Start - 5 Minutes to Solar Optimization

Get your Home Assistant integration running in 5 minutes!

## ⚡ Super Quick Installation

### 1. Copy Integration (30 seconds)

```bash
# If on same machine as Home Assistant
cp -r homeassistant-integration/custom_components/electricity_forecast \
      /config/custom_components/

# Or if remote (replace with your HA host)
scp -r homeassistant-integration/custom_components/electricity_forecast \
      homeassistant.local:/config/custom_components/
```

### 2. Restart Home Assistant (1 minute)

Settings → System → Restart

### 3. Add Integration (2 minutes)

1. Settings → Devices & Services
2. **+ Add Integration**
3. Search: **"Electricity Price Forecast"**
4. Enter:
   - API URL: `http://YOUR_API_HOST:8000`
   - Region: `DE` (or your region)
5. Submit ✅

### 4. Verify (30 seconds)

Developer Tools → States → Search: `electricity_forecast`

You should see 8 sensors! 🎉

### 5. Add Dashboard (1 minute)

Copy-paste this into a new Lovelace card:

```yaml
type: entities
title: ⚡ Electricity Prices
entities:
  - sensor.electricity_forecast_de_current_price
  - sensor.electricity_forecast_de_next_hour_price
  - sensor.electricity_forecast_de_recommendation
  - sensor.electricity_forecast_de_cheapest_hour
```

## 🔋 First Automation - Smart Battery Charging

```yaml
# automations.yaml
- alias: "Smart Battery Charge"
  trigger:
    - platform: state
      entity_id: sensor.electricity_forecast_de_recommendation
      to: "charge"
  action:
    - service: switch.turn_on
      entity_id: switch.battery_charger
    - service: notify.mobile_app
      data:
        message: "⚡ Charging - Price is {{ states('sensor.electricity_forecast_de_current_price') }} EUR/MWh"
```

## 📊 What You Get

### 8 Sensors Created:

| Sensor | What It Does |
|--------|-------------|
| **Current Price** | Real-time electricity price |
| **Next Hour Price** | Price coming up next |
| **Average Price Today** | Today's average (compare vs current) |
| **Cheapest Hour** | Best time to charge |
| **Expensive Hour** | When to use stored energy |
| **Price Trend** | Rising, falling, or stable |
| **Recommendation** | charge/discharge/neutral |
| **Forecast** | Full 24h/7d data in attributes |

### Smart Recommendations:

- **charge** = Price in bottom 25% → Charge batteries, run appliances
- **discharge** = Price in top 25% → Use stored energy, sell to grid
- **neutral** = Average price → Business as usual

## 🎯 Use Cases

### For Solar Panel Owners:

1. **Battery Optimization**
   - Charge during cheap hours
   - Discharge during expensive hours
   - Maximize ROI

2. **Appliance Scheduling**
   - Run dishwasher during cheapest 3 hours
   - Charge EV when price drops
   - Heat water tank at optimal times

3. **Grid Trading**
   - Buy when cheap, sell when expensive
   - Automated based on forecasts

## 🔧 Troubleshooting

### "Integration not found"
→ Files not in right place or forgot to restart
→ Check: `/config/custom_components/electricity_forecast/`

### "Cannot connect to API"
→ API not running or wrong URL
→ Test: `curl http://YOUR_API_HOST:8000/health`

### "Sensors unavailable"
→ No cached predictions
→ Run: `python prediction-service/pregenerate_predictions.py`

## 📚 Full Documentation

- **[README.md](README.md)** - Complete features & examples
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Detailed setup
- **[PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md)** - Share with community

## 🚀 Next Steps

1. ✅ Set up automations for your battery/appliances
2. ✅ Create beautiful dashboard with price charts
3. ✅ Monitor your savings!
4. ✅ Share your setup in Home Assistant community

## 💡 Pro Tips

- Update frequency: 15 min (configure in `__init__.py`)
- Run data ingestion hourly via cron
- Retrain model weekly for best accuracy
- Use cheapest 3 hours for heavy appliances

## ❤️ Support

- Issues: [GitHub Issues](https://github.com/your-username/electricity-forecast-ha/issues)
- Questions: Home Assistant Community Forum
- Feature Requests: Welcome!

Enjoy optimizing your energy usage! ⚡💰
