# Installation Guide - Electricity Price Forecast for Home Assistant

## Quick Start (5 Minutes)

### Step 1: Ensure Your API is Running

Before installing the integration, make sure your Electricity Forecast API is accessible:

```bash
# Test from your Home Assistant machine
curl http://YOUR_API_HOST:8000/health

# Expected response:
# {"status":"healthy","mode":"cache-only","regions_available":8,...}
```

If the API isn't running, start it:

```bash
cd /path/to/weather-forecast

# Start the API
INFLUXDB_TOKEN=your-token INFLUXDB_URL=http://your-host:8086 \
  python api-service/api_enhanced.py

# Or run in background with systemd (recommended for production)
```

### Step 2: Install Integration

#### Option A: Via HACS (Easiest - Coming Soon)

1. Open **HACS** → **Integrations**
2. Click **⋮** (three dots) → **Custom repositories**
3. Add: `https://github.com/YOUR-USERNAME/electricity-forecast-ha`
4. Category: **Integration**
5. Search for **"Electricity Price Forecast"**
6. Click **Download**
7. **Restart Home Assistant**

#### Option B: Manual Installation (Works Now)

1. **Copy files to Home Assistant**:

   If Home Assistant is on the same machine:
   ```bash
   cp -r homeassistant-integration/custom_components/electricity_forecast \
         /config/custom_components/
   ```

   If Home Assistant is remote (via SSH):
   ```bash
   scp -r homeassistant-integration/custom_components/electricity_forecast \
         your-ha-host:/config/custom_components/
   ```

   If using Home Assistant OS (via Samba share):
   - Connect to `\\homeassistant.local\config`
   - Copy `custom_components/electricity_forecast` folder to the share

2. **Restart Home Assistant**:
   - Settings → System → Restart

### Step 3: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **"Electricity Price Forecast"**
4. Enter configuration:
   - **API URL**: `http://YOUR_API_HOST:8000`
     - If API is on same machine: `http://homeassistant.local:8000`
     - If API is on another machine: `http://192.168.1.X:8000`
   - **Region**: Select your region (e.g., `DE`)
5. Click **Submit**

### Step 4: Verify Installation

Check that sensors are working:

1. Go to **Developer Tools** → **States**
2. Search for `electricity_forecast`
3. You should see 8 sensors:
   - `sensor.electricity_forecast_de_current_price`
   - `sensor.electricity_forecast_de_next_hour_price`
   - `sensor.electricity_forecast_de_avg_price_today`
   - `sensor.electricity_forecast_de_cheapest_hour`
   - `sensor.electricity_forecast_de_expensive_hour`
   - `sensor.electricity_forecast_de_price_trend`
   - `sensor.electricity_forecast_de_recommendation`
   - `sensor.electricity_forecast_de_forecast`

## Example Dashboard

### Copy-Paste Ready Lovelace Card

Add this to your Lovelace dashboard:

```yaml
type: vertical-stack
cards:
  # Current Status Card
  - type: entities
    title: ⚡ Electricity Prices
    show_header_toggle: false
    entities:
      - entity: sensor.electricity_forecast_de_current_price
        name: Current Price
        icon: mdi:cash
      - entity: sensor.electricity_forecast_de_next_hour_price
        name: Next Hour
        icon: mdi:clock-fast
      - entity: sensor.electricity_forecast_de_price_trend
        name: Trend
        icon: mdi:trending-up
      - type: divider
      - entity: sensor.electricity_forecast_de_recommendation
        name: Recommendation
        icon: mdi:lightbulb

  # Today's Statistics
  - type: entities
    title: 📊 Today's Statistics
    show_header_toggle: false
    entities:
      - entity: sensor.electricity_forecast_de_avg_price_today
        name: Average Price
        icon: mdi:chart-line
      - entity: sensor.electricity_forecast_de_cheapest_hour
        name: Cheapest Hour
        icon: mdi:arrow-down-bold
      - entity: sensor.electricity_forecast_de_expensive_hour
        name: Most Expensive Hour
        icon: mdi:arrow-up-bold

  # Gauge Cards for Visual Representation
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.electricity_forecast_de_current_price
        name: Current
        min: 0
        max: 150
        severity:
          green: 0
          yellow: 80
          red: 120
      - type: gauge
        entity: sensor.electricity_forecast_de_next_hour_price
        name: Next Hour
        min: 0
        max: 150
        severity:
          green: 0
          yellow: 80
          red: 120
```

### Advanced: Price Chart (Requires ApexCharts Card)

First install [ApexCharts Card](https://github.com/RomRider/apexcharts-card) via HACS.

Then add this card:

```yaml
type: custom:apexcharts-card
header:
  title: 24-Hour Price Forecast
  show: true
  show_states: true
  colorize_states: true
graph_span: 24h
span:
  start: hour
now:
  show: true
  label: Now
series:
  - entity: sensor.electricity_forecast_de_forecast
    name: Forecast
    type: line
    color: orange
    stroke_width: 2
    data_generator: |
      return entity.attributes.forecast_24h.map((item) => {
        return [new Date(item.time).getTime(), item.price];
      });
  - entity: sensor.electricity_forecast_de_avg_price_today
    name: Average
    type: line
    color: gray
    stroke_width: 1
    extend_to: now
```

## Automation Examples

### 1. Smart Battery Charging

```yaml
# automations.yaml

# Start charging during cheap hours
- id: charge_battery_cheap
  alias: "Charge Battery - Cheap Price"
  trigger:
    - platform: state
      entity_id: sensor.electricity_forecast_de_recommendation
      to: "charge"
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.battery_charger
    - service: notify.mobile_app_your_phone
      data:
        title: "⚡ Battery Charging"
        message: "Price: {{ states('sensor.electricity_forecast_de_current_price') }} EUR/MWh"

# Stop charging when price rises
- id: stop_charge_expensive
  alias: "Stop Charging - Price Rising"
  trigger:
    - platform: state
      entity_id: sensor.electricity_forecast_de_recommendation
      from: "charge"
  action:
    - service: switch.turn_off
      target:
        entity_id: switch.battery_charger
```

### 2. Dishwasher Scheduling

```yaml
# Run dishwasher during one of the 3 cheapest hours
- id: smart_dishwasher
  alias: "Smart Dishwasher"
  trigger:
    - platform: time_pattern
      hours: "*"
      minutes: "5"
  condition:
    # Only if dishwasher is ready (door closed, delay start enabled)
    - condition: state
      entity_id: binary_sensor.dishwasher_ready
      state: "on"
    # Check if current hour is in cheapest 3 hours
    - condition: template
      value_template: >
        {% set cheapest = state_attr('sensor.electricity_forecast_de_cheapest_hour', 'cheapest_hours_today') %}
        {% if cheapest %}
          {% set current_hour = now().hour %}
          {% set cheap_hours = cheapest | map(attribute='time') | map('regex_replace', '.*T(\d{2}):.*', '\\1') | map('int') | list %}
          {{ current_hour in cheap_hours }}
        {% else %}
          false
        {% endif %}
  action:
    - service: button.press
      target:
        entity_id: button.dishwasher_start
```

### 3. Price Alert Notifications

```yaml
# Alert when price drops below threshold
- id: low_price_alert
  alias: "Low Price Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.electricity_forecast_de_current_price
      below: 50
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "💰 Electricity Price Alert"
        message: >
          Price dropped to {{ states('sensor.electricity_forecast_de_current_price') }} EUR/MWh!
          Great time to:
          - Charge EV battery
          - Run washing machine
          - Heat water tank
        data:
          actions:
            - action: "CHARGE_BATTERY"
              title: "Charge Battery"
```

## Troubleshooting

### "Integration not found"

**Problem**: Integration doesn't appear in the Add Integration dialog.

**Solution**:
1. Verify files are in correct location:
   ```bash
   ls /config/custom_components/electricity_forecast/
   # Should show: __init__.py, manifest.json, sensor.py, etc.
   ```
2. Restart Home Assistant completely (not just reload)
3. Clear browser cache (Ctrl+Shift+R)

### "Cannot connect to API"

**Problem**: Configuration fails with connection error.

**Solution**:
1. Test API from Home Assistant machine:
   ```bash
   # SSH into Home Assistant
   ssh root@homeassistant.local

   # Test API
   curl http://YOUR_API_HOST:8000/health
   ```

2. Check firewall rules:
   ```bash
   # On API host, ensure port 8000 is open
   sudo ufw allow 8000/tcp
   ```

3. If Home Assistant is in Docker/container:
   - Don't use `localhost` or `127.0.0.1`
   - Use host IP: `http://192.168.1.X:8000`
   - Or use: `http://host.docker.internal:8000` (Docker Desktop)

### "Sensors show unavailable"

**Problem**: Sensors exist but show "Unavailable".

**Solution**:
1. Check that predictions are cached:
   ```bash
   curl http://YOUR_API_HOST:8000/api/predictions/DE/next-24h
   ```

2. If empty, run prediction generator:
   ```bash
   cd /path/to/weather-forecast
   INFLUXDB_TOKEN=xxx INFLUXDB_URL=xxx \
     python prediction-service/pregenerate_predictions.py
   ```

3. Verify data ingestion has run:
   ```bash
   INFLUXDB_TOKEN=xxx INFLUXDB_URL=xxx \
     python data-ingestion-service/ingest_all_regions.py --mode auto
   ```

4. Check Home Assistant logs:
   - Settings → System → Logs
   - Search for "electricity_forecast"

### "No forecast data"

**Problem**: Forecast sensor has empty attributes.

**Solution**:
Ensure forecast weather data is fetched:
```bash
# The default already fetches 7-day forecast
python data-ingestion-service/ingest_all_regions.py --mode auto

# Verify forecast exists
curl http://YOUR_API_HOST:8000/api/forecast/DE/weather?hours=24
```

## Network Configuration

### Finding Your API Host IP

```bash
# On the machine running the API
hostname -I
# Output: 192.168.1.100 ...

# Use this IP in Home Assistant config
# API URL: http://192.168.1.100:8000
```

### Making API Accessible

If API and Home Assistant are on different machines:

1. **Configure API to listen on all interfaces**:
   ```bash
   # api_enhanced.py already uses 0.0.0.0:8000
   # This allows connections from any IP
   ```

2. **Open firewall on API host**:
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 8000/tcp

   # Check status
   sudo ufw status
   ```

3. **Test connectivity**:
   ```bash
   # From Home Assistant machine
   curl http://API_HOST_IP:8000/health
   ```

## Production Setup

### Running API as Systemd Service

Create `/etc/systemd/system/electricity-forecast-api.service`:

```ini
[Unit]
Description=Electricity Forecast API
After=network.target influxdb.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/weather-forecast/api-service
Environment="INFLUXDB_TOKEN=your-token"
Environment="INFLUXDB_URL=http://localhost:8086"
ExecStart=/usr/bin/python3 api_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable electricity-forecast-api
sudo systemctl start electricity-forecast-api
sudo systemctl status electricity-forecast-api
```

### Cron Jobs for Data Updates

Add to crontab:
```bash
crontab -e
```

```bash
# Run data ingestion every hour
5 * * * * cd /path/to/weather-forecast && INFLUXDB_TOKEN=xxx INFLUXDB_URL=xxx python data-ingestion-service/ingest_all_regions.py --mode auto >> /var/log/forecast-ingestion.log 2>&1

# Run prediction generator every hour (5 min after ingestion)
10 * * * * cd /path/to/weather-forecast && INFLUXDB_TOKEN=xxx INFLUXDB_URL=xxx python prediction-service/pregenerate_predictions.py >> /var/log/forecast-predictions.log 2>&1

# Retrain model daily at 2 AM
0 2 * * * cd /path/to/weather-forecast && INFLUXDB_TOKEN=xxx INFLUXDB_URL=xxx python training-service/train_model.py >> /var/log/forecast-training.log 2>&1
```

## Next Steps

1. **Set up automations** for your solar battery or appliances
2. **Create beautiful dashboards** with price charts
3. **Monitor your savings** by tracking when you charge vs discharge
4. **Share your setup** in the Home Assistant community!

## Support

- **Questions**: Open an issue on GitHub
- **Bug reports**: Provide Home Assistant logs + API logs
- **Feature requests**: Describe your use case

## Additional Resources

- [Home Assistant Automation Guide](https://www.home-assistant.io/docs/automation/)
- [Lovelace Dashboard Guide](https://www.home-assistant.io/lovelace/)
- [Template Sensor Documentation](https://www.home-assistant.io/integrations/template/)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card)
