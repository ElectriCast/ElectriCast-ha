# Electricity Price Forecast - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration that provides electricity price forecasts for German regions. Perfect for optimizing solar panel battery charging, smart appliance scheduling, and energy cost management.

## Features

### 9 Useful Sensors

1. **Current Price** - Real-time electricity price
2. **Next Hour Price** - Price for the next hour (for immediate decisions)
3. **Average Price Today** - Today's average price with min/max
4. **Cheapest Hour Today** - Best time to charge batteries or run appliances
5. **Most Expensive Hour Today** - When to use stored energy
6. **Price Trend** - Rising, falling, or stable
7. **Recommendation** - Smart action recommendation (charge/discharge/hold)
8. **Forecast** - Full 24h and 7-day forecasts as attributes
9. **7 Day Price Forecast** - Dedicated sensor with 7-day price predictions and daily averages

### Smart Recommendations

The integration provides actionable recommendations based on price analysis:
- **Charge** - Current price is in the bottom 25% (great time to charge batteries/run appliances)
- **Discharge** - Current price is in the top 25% (good time to use stored energy or sell to grid)
- **Neutral (cheap/expensive)** - Price is moderate

### All German Regions Supported

- DE - Germany (National Average)
- DE-BY - Bavaria (Bayern)
- DE-BW - Baden-Württemberg
- DE-NW - North Rhine-Westphalia (NRW)
- DE-NI - Lower Saxony (Niedersachsen)
- DE-HE - Hesse (Hessen)
- DE-BE - Berlin & Brandenburg
- DE-HH - Hamburg & Schleswig-Holstein

## Installation

### Method 1: HACS (Recommended)

1. **Add Custom Repository to HACS**:
   - Open HACS in Home Assistant
   - Click on "Integrations"
   - Click the three dots (⋮) in the top right
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/YOUR-USERNAME/electricity-forecast-ha`
   - Category: "Integration"
   - Click "Add"

2. **Install via HACS**:
   - Click "Explore & Download Repositories"
   - Search for "Electricity Price Forecast"
   - Click "Download"
   - Restart Home Assistant

### Method 2: Manual Installation

1. **Copy files to Home Assistant**:
   ```bash
   # Copy the entire custom_components folder to your Home Assistant config directory
   cp -r homeassistant-integration/custom_components/electricity_forecast \
         /config/custom_components/
   ```

2. **Restart Home Assistant**

## Configuration

### Prerequisites

Make sure your Electricity Forecast API is running and accessible from Home Assistant:

```bash
# Start the API service
cd /path/to/weather-forecast
INFLUXDB_TOKEN=your-token INFLUXDB_URL=http://your-host:8086 \
  python api-service/api_enhanced.py
```

> 💡 **Need help configuring the API URL?** See the detailed [API Configuration Guide](API_CONFIGURATION.md) for network scenarios, troubleshooting, and best practices.

### Setup via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Electricity Price Forecast"**
4. Enter your configuration:
   - **API Root URL**: The root URL of your API server (e.g., `http://192.168.1.100:8000`)
     - Use your server's IP address or hostname
     - Include the port (default: 8000)
     - Do NOT include trailing slash
     - Examples: `http://192.168.1.100:8000`, `http://localhost:8000`, `http://my-server.local:8000`
   - **Region**: Select your region (e.g., `DE` for Germany)
5. Click **Submit**

The integration will validate the connection by:
- Testing the `/health` endpoint
- Fetching a sample prediction for your region
- Verifying data is available

### Reconfiguring API URL

To change the API URL or region after initial setup:

1. Go to **Settings** → **Devices & Services**
2. Find the **Electricity Price Forecast** integration
3. Click the **three dots (⋮)** menu
4. Select **Configure**
5. Update the **API Root URL** or **Region**
6. Click **Submit**

The integration will automatically reload with the new settings.

### Setup via YAML (Alternative)

Add to your `configuration.yaml`:

```yaml
# configuration.yaml
electricity_forecast:
  api_url: "http://192.168.1.100:8000"
  region_id: "DE"
```

Restart Home Assistant after adding the configuration.

## Available Sensors

After installation, you'll have these sensors:

| Entity ID | Description | Unit |
|-----------|-------------|------|
| `sensor.electricity_forecast_de_current_price` | Current electricity price | EUR/MWh |
| `sensor.electricity_forecast_de_next_hour_price` | Next hour price | EUR/MWh |
| `sensor.electricity_forecast_de_avg_price_today` | Average price today | EUR/MWh |
| `sensor.electricity_forecast_de_cheapest_hour` | Cheapest hour today | EUR/MWh |
| `sensor.electricity_forecast_de_expensive_hour` | Most expensive hour today | EUR/MWh |
| `sensor.electricity_forecast_de_price_trend` | Price trend (rising/falling/stable) | - |
| `sensor.electricity_forecast_de_recommendation` | Action recommendation | - |
| `sensor.electricity_forecast_de_forecast` | Full forecast data | EUR/MWh |
| `sensor.electricity_forecast_de_7day_forecast` | 7-day price forecast with daily averages | EUR/MWh |

## Usage Examples

### 1. Display Current Price in Lovelace

```yaml
# ui-lovelace.yaml
type: entities
title: Electricity Prices
entities:
  - entity: sensor.electricity_forecast_de_current_price
    name: Current Price
  - entity: sensor.electricity_forecast_de_next_hour_price
    name: Next Hour
  - entity: sensor.electricity_forecast_de_avg_price_today
    name: Today's Average
  - entity: sensor.electricity_forecast_de_recommendation
    name: Recommendation
```

### 2. Price Chart (ApexCharts Card)

Install the [ApexCharts Card](https://github.com/RomRider/apexcharts-card) first:

```yaml
type: custom:apexcharts-card
header:
  title: 24h Price Forecast
  show: true
graph_span: 24h
span:
  start: hour
series:
  - entity: sensor.electricity_forecast_de_forecast
    data_generator: |
      return entity.attributes.forecast_24h.map((item) => {
        return [new Date(item.time).getTime(), item.price];
      });
    name: Price Forecast
    color: orange
```

### 2b. 7-Day Price Chart (ApexCharts Card)

```yaml
type: custom:apexcharts-card
header:
  title: 7-Day Price Forecast
  show: true
graph_span: 7d
series:
  - entity: sensor.electricity_forecast_de_7day_forecast
    data_generator: |
      return entity.attributes.forecast_7d_full.map((item) => {
        return [new Date(item.time).getTime(), item.price];
      });
    name: 7-Day Forecast
    color: blue
    stroke_width: 2
  - entity: sensor.electricity_forecast_de_7day_forecast
    data_generator: |
      return entity.attributes.daily_averages.map((item) => {
        return [new Date(item.date).getTime(), item.avg_price];
      });
    name: Daily Average
    color: orange
    stroke_width: 3
    type: line
```

### 3. Automation: Charge Battery at Cheapest Hours

```yaml
# automations.yaml
- alias: "Charge Battery During Cheap Hours"
  trigger:
    - platform: state
      entity_id: sensor.electricity_forecast_de_recommendation
      to: "charge"
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.battery_charging
    - service: notify.mobile_app
      data:
        message: "⚡ Charging battery - electricity is cheap!"

- alias: "Stop Charging When Price Rises"
  trigger:
    - platform: state
      entity_id: sensor.electricity_forecast_de_recommendation
      from: "charge"
  action:
    - service: switch.turn_off
      target:
        entity_id: switch.battery_charging
```

### 4. Automation: Smart Appliance Scheduling

```yaml
# Run dishwasher during cheapest 3 hours
- alias: "Smart Dishwasher Scheduling"
  trigger:
    - platform: time_pattern
      hours: "*"
  condition:
    - condition: template
      value_template: >
        {% set cheapest_hours = state_attr('sensor.electricity_forecast_de_cheapest_hour', 'cheapest_hours_today') %}
        {% set current_time = now().isoformat() %}
        {{ current_time in cheapest_hours | map(attribute='time') | list }}
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.dishwasher
```

### 5. Notification: Price Alerts

```yaml
- alias: "Alert When Prices Are Very Low"
  trigger:
    - platform: numeric_state
      entity_id: sensor.electricity_forecast_de_current_price
      below: 50  # EUR/MWh
  action:
    - service: notify.mobile_app
      data:
        title: "💰 Low Electricity Price Alert"
        message: >
          Price is {{ states('sensor.electricity_forecast_de_current_price') }} EUR/MWh
          Great time to charge your battery or run appliances!
```

### 6. Template Sensor: Is Price Below Average?

```yaml
# configuration.yaml
template:
  - sensor:
      - name: "Price Below Average"
        state: >
          {% set current = states('sensor.electricity_forecast_de_current_price') | float %}
          {% set average = states('sensor.electricity_forecast_de_avg_price_today') | float %}
          {{ current < average }}
```

### 7. Weekly Planning: High-Energy Tasks During Cheap Days

```yaml
# Automation to notify about cheapest days in the week for planning
- alias: "Weekly Price Report"
  trigger:
    - platform: time
      at: "07:00:00"
    - platform: time
      at: "19:00:00"
  action:
    - service: notify.mobile_app
      data:
        title: "Weekly Price Forecast"
        message: >
          7-Day Average: {{ states('sensor.electricity_forecast_de_7day_forecast') }} EUR/MWh
          This Week: {{ state_attr('sensor.electricity_forecast_de_7day_forecast', 'min_price_7d') }} -
          {{ state_attr('sensor.electricity_forecast_de_7day_forecast', 'max_price_7d') }} EUR/MWh

          {% set daily_avg = state_attr('sensor.electricity_forecast_de_7day_forecast', 'daily_averages') %}
          Cheapest Day: {{ daily_avg | sort(attribute='avg_price') | first }}
```

### 8. Template Sensor: Cheapest Day This Week

```yaml
# configuration.yaml
template:
  - sensor:
      - name: "Cheapest Day This Week"
        state: >
          {% set daily_avg = state_attr('sensor.electricity_forecast_de_7day_forecast', 'daily_averages') %}
          {% if daily_avg %}
            {{ (daily_avg | sort(attribute='avg_price') | first).date }}
          {% else %}
            unavailable
          {% endif %}
        attributes:
          price: >
            {% set daily_avg = state_attr('sensor.electricity_forecast_de_7day_forecast', 'daily_averages') %}
            {% if daily_avg %}
              {{ (daily_avg | sort(attribute='avg_price') | first).avg_price }}
            {% else %}
              unavailable
            {% endif %}
```

### 9. Advanced: Energy Dashboard Integration

```yaml
# configuration.yaml
utility_meter:
  electricity_cost_tracker:
    source: sensor.electricity_forecast_de_current_price
    cycle: daily
```

## Sensor Attributes

Many sensors provide additional data as attributes:

### Current Price
```yaml
last_updated: "2025-10-17T22:00:00Z"
region: "DE"
```

### Cheapest Hour Today
```yaml
cheapest_time: "2025-10-18T03:00:00Z"
cheapest_hours_today:
  - time: "2025-10-18T03:00:00Z"
    price: 54.85
  - time: "2025-10-18T04:00:00Z"
    price: 56.23
  - time: "2025-10-18T02:00:00Z"
    price: 58.12
```

### Forecast Sensor
```yaml
forecast_24h:
  - time: "2025-10-17T22:00:00Z"
    price: 66.94
    conf_lower: 50.20
    conf_upper: 83.68
  # ... more hours
forecast_7d:
  - time: "2025-10-17T22:00:00Z"
    price: 66.94
  # ... more hours
forecast_24h_count: 24
forecast_7d_count: 168
```

### Recommendation Sensor
```yaml
description: "Good time to charge batteries or run appliances"
icon_suggestion: "mdi:battery-charging"
```

### 7-Day Forecast Sensor
```yaml
forecast_7d_full:
  - time: "2025-10-17T22:00:00Z"
    price: 66.94
  - time: "2025-10-17T23:00:00Z"
    price: 64.12
  # ... 168 hours total
daily_averages:
  - date: "2025-10-17"
    avg_price: 75.23
    min_price: 54.85
    max_price: 92.40
  - date: "2025-10-18"
    avg_price: 68.15
    min_price: 52.30
    max_price: 88.70
  # ... 7 days total
min_price_7d: 52.30
max_price_7d: 95.60
avg_price_7d: 71.45
total_hours: 168
region: "DE"
```

## Solar Panel Optimization Use Cases

### 1. Battery Charging Strategy
- **Charge** when recommendation is "charge" (bottom 25% prices)
- **Hold** when prices are moderate
- **Discharge** when recommendation is "discharge" (top 25% prices)

### 2. Grid Feed-in Timing
- Export excess solar during expensive hours
- Store energy during cheap hours for later use

### 3. Load Shifting
- Schedule heavy appliances (washing machine, dishwasher, EV charging) during cheap hours
- Avoid usage during expensive hours

### 4. Smart Home Automation
- Preheat water heater during cheap hours
- Adjust climate control based on price forecasts
- Optimize heat pump operation

## Troubleshooting

### Integration Not Showing Up

1. Check that files are in the correct location:
   ```
   /config/custom_components/electricity_forecast/
   ```

2. Restart Home Assistant

3. Check logs:
   ```
   Settings → System → Logs
   ```

### Cannot Connect to API

**Error: "Failed to connect to the API"**

1. **Verify API is running:**
   ```bash
   curl http://your-api-url:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **Check API URL format:**
   - ✅ Correct: `http://192.168.1.100:8000`
   - ✅ Correct: `http://localhost:8000`
   - ❌ Wrong: `http://192.168.1.100:8000/` (trailing slash)
   - ❌ Wrong: `192.168.1.100:8000` (missing http://)
   - ❌ Wrong: `http://192.168.1.100` (missing port)

3. **Test network connectivity from Home Assistant:**
   - If HA is running in Docker/container, use the host's IP address
   - Do NOT use `localhost` if API runs on host and HA in container
   - Use `http://host.docker.internal:8000` for Docker Desktop
   - Use `http://192.168.x.x:8000` for the actual LAN IP

4. **Check firewall settings:**
   - Port 8000 must be accessible from Home Assistant
   - Test with: `curl http://your-ip:8000/health` from HA container

5. **Verify API endpoints work:**
   ```bash
   # Test health
   curl http://your-ip:8000/health

   # Test predictions
   curl http://your-ip:8000/api/predictions/DE/next-24h
   ```

### Error: "Invalid URL format"

- Make sure URL starts with `http://` or `https://`
- Include the port number (usually 8000)
- Remove any trailing slashes
- Example: `http://192.168.1.100:8000`

### Sensors Show "Unavailable"

1. Check API health endpoint:
   ```bash
   curl http://your-api-url:8000/api/predictions/DE/next-24h
   ```

2. Verify predictions are cached:
   ```bash
   # Run prediction generator
   python prediction-service/pregenerate_predictions.py
   ```

3. Check integration logs in Home Assistant

### Forecast Data Missing

Make sure the data ingestion service has fetched forecast data:
```bash
python data-ingestion-service/ingest_all_regions.py --mode auto
```

## Publishing to HACS

### Prerequisites

1. Create a GitHub repository for your integration
2. Repository name should be descriptive (e.g., `electricity-forecast-ha`)

### Repository Structure

```
electricity-forecast-ha/
├── custom_components/
│   └── electricity_forecast/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── sensor.py
│       ├── api.py
│       ├── services.yaml
│       └── translations/
│           └── en.json
├── README.md
├── LICENSE
├── hacs.json
└── .github/
    └── workflows/
        └── validate.yaml
```

### Step 1: Create hacs.json

```json
{
  "name": "Electricity Price Forecast",
  "render_readme": true,
  "domains": ["sensor"],
  "homeassistant": "2023.1.0",
  "iot_class": "cloud_polling"
}
```

### Step 2: Add Validation Workflow

Create `.github/workflows/validate.yaml`:

```yaml
name: Validate

on:
  push:
  pull_request:
  schedule:
    - cron: "0 0 * * *"

jobs:
  validate:
    runs-on: "ubuntu-latest"
    steps:
      - uses: "actions/checkout@v3"
      - name: HACS validation
        uses: "hacs/action@main"
        with:
          category: "integration"
```

### Step 3: Create Release

1. Tag your code:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

2. Create GitHub release from the tag

### Step 4: Submit to HACS

1. Fork the [HACS repository](https://github.com/hacs/default)

2. Add your repository to `custom_components.json`:
   ```json
   {
     "your-username/electricity-forecast-ha": {
       "name": "Electricity Price Forecast",
       "domains": ["sensor"],
       "iot_class": "cloud_polling"
     }
   }
   ```

3. Create pull request

4. Wait for HACS team review

### Step 5: Promote Your Integration

- Add screenshots to README
- Create documentation website
- Share on Home Assistant forums
- Post in r/homeassistant

## API Reference

The integration communicates with these API endpoints:

- `GET /health` - API health check
- `GET /api/predictions/{region_id}/next-24h` - 24h forecast
- `GET /api/predictions/{region_id}/next-7d` - 7-day forecast
- `GET /api/historical/{region_id}/combined` - Historical data

## Update Frequency

- Sensors update every **15 minutes** by default
- Change in `__init__.py`: `SCAN_INTERVAL = timedelta(minutes=X)`

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/electricity-forecast-ha/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/electricity-forecast-ha/discussions)
- **Home Assistant Forum**: [Community Thread](https://community.home-assistant.io/)

## License

MIT License - see LICENSE file

## Credits

Developed for optimizing solar panel battery management and reducing electricity costs.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Changelog

### Version 1.1.0
- Added dedicated 7-Day Price Forecast sensor with daily averages
- Enhanced forecast attributes with min/max prices for the week
- Added usage examples for weekly price planning
- New template sensor examples for cheapest day detection
- Improved configuration UI with better API URL descriptions and validation
- Added options flow to reconfigure API URL and region after initial setup
- Better error messages for API connection issues
- URL format validation with helpful error messages

### Version 1.0.0
- Initial release
- 8 sensor entities
- Configuration flow
- Support for all 8 German regions
- Smart recommendations for battery management
