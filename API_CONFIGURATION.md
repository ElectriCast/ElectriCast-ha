# API Configuration Guide

This guide explains how to configure the API Root URL for the Electricity Price Forecast integration.

## What is the API Root URL?

The API Root URL is the base address where your Electricity Forecast API service is running. This is the server that provides the price predictions and historical data.

## URL Format

The URL should follow this format:

```
http://[hostname or IP]:[port]
```

### Valid Examples

✅ **Correct URLs:**
- `http://192.168.1.100:8000` - Local network IP
- `http://localhost:8000` - Local machine (only if HA and API on same host)
- `http://my-server.local:8000` - Local hostname
- `http://10.0.0.50:8000` - Different local IP
- `https://api.example.com:8443` - HTTPS with custom port

### Invalid Examples

❌ **Incorrect URLs:**
- `http://192.168.1.100:8000/` - Has trailing slash
- `192.168.1.100:8000` - Missing protocol (http://)
- `http://192.168.1.100` - Missing port number
- `http://192.168.1.100:8000/api` - Don't include path
- `localhost:8000` - Missing protocol

## Network Scenarios

### Scenario 1: Everything on the Same Machine
- **Setup**: API and Home Assistant on the same physical/virtual machine
- **URL**: `http://localhost:8000`
- **Works**: ✅ Always works

### Scenario 2: Home Assistant in Docker, API on Host
- **Setup**: HA in Docker container, API running on the host machine
- **URL**:
  - Docker Desktop: `http://host.docker.internal:8000`
  - Linux: `http://172.17.0.1:8000` or use host's LAN IP
- **Don't use**: ❌ `http://localhost:8000` (won't work)

### Scenario 3: Different Machines on Same Network
- **Setup**: HA on one device, API on another device
- **URL**: `http://[API-machine-IP]:8000`
- **Example**: `http://192.168.1.100:8000`
- **How to find IP**: Run `hostname -I` on the API machine

### Scenario 4: Remote API Server
- **Setup**: API hosted on a remote server or cloud
- **URL**: `http://[server-domain-or-IP]:8000`
- **Example**: `https://my-forecast-api.example.com:8000`
- **Note**: Ensure firewall allows incoming connections on port 8000

## Port Numbers

The default API port is **8000**. However, you can change this when starting the API service:

```bash
# Default port 8000
python api-service/api_enhanced.py

# Custom port 3000
uvicorn api_enhanced:app --host 0.0.0.0 --port 3000
```

If you use a custom port, update the URL accordingly:
- Default: `http://192.168.1.100:8000`
- Custom: `http://192.168.1.100:3000`

## Testing Your API URL

Before configuring the integration, test your API URL:

### 1. Test Health Endpoint
```bash
curl http://your-api-url:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test Predictions Endpoint
```bash
curl http://your-api-url:8000/api/predictions/DE/next-24h
```

Expected response: Array of price predictions

### 3. Test from Home Assistant Container

If Home Assistant is in Docker, test from inside the container:

```bash
# Enter HA container
docker exec -it homeassistant /bin/bash

# Test connection
curl http://your-api-url:8000/health
```

## Common Issues and Solutions

### Issue: "Cannot connect to API"

**Possible causes:**
1. API service is not running
2. Wrong IP address or port
3. Firewall blocking the connection
4. Network connectivity issue

**Solutions:**
1. Start the API service:
   ```bash
   cd /path/to/weather-forecast
   INFLUXDB_TOKEN=your-token INFLUXDB_URL=http://your-host:8086 \
     python api-service/api_enhanced.py
   ```

2. Verify API is accessible:
   ```bash
   curl http://your-ip:8000/health
   ```

3. Check firewall:
   ```bash
   # Allow port 8000 (example for Ubuntu/Debian)
   sudo ufw allow 8000/tcp
   ```

4. Test from HA host:
   ```bash
   # If HA is in Docker, test from host first
   curl http://localhost:8000/health
   ```

### Issue: "Invalid URL format"

**Solution:** Check the URL follows the correct format:
- Must start with `http://` or `https://`
- Must include port number
- Must NOT have trailing slash
- Example: `http://192.168.1.100:8000`

### Issue: API works locally but not from Home Assistant

**Possible causes:**
1. HA is in Docker and using `localhost`
2. Firewall blocking external access
3. API only listening on localhost

**Solutions:**
1. Use host's LAN IP instead of localhost
2. Configure firewall to allow port 8000
3. Start API with `--host 0.0.0.0`:
   ```bash
   python api-service/api_enhanced.py --host 0.0.0.0 --port 8000
   ```

## Configuration Steps

### Initial Setup

1. **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Electricity Price Forecast"**
4. Enter:
   - **API Root URL**: `http://your-ip:8000`
   - **Region**: Your region (e.g., `DE`)
5. Click **Submit**

### Reconfiguring URL

1. **Settings** → **Devices & Services**
2. Find **Electricity Price Forecast**
3. Click **⋮** (three dots)
4. Select **Configure**
5. Update **API Root URL**
6. Click **Submit**

The integration will automatically reload with the new URL.

## Security Considerations

### HTTP vs HTTPS

- **Development/Home Network**: `http://` is fine
- **Production/Public Network**: Use `https://` with SSL certificate

### Firewall Rules

Only expose port 8000 to trusted networks:

```bash
# Allow only local network (example)
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Or allow specific IP
sudo ufw allow from 192.168.1.50 to any port 8000
```

### Authentication

Currently, the API doesn't require authentication. If exposing to the internet, consider:
- Using a reverse proxy (nginx, Caddy)
- Adding API key authentication
- Using VPN for remote access

## Advanced: Running API as a Service

For production use, run the API as a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/electricity-forecast-api.service
```

```ini
[Unit]
Description=Electricity Forecast API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/weather-forecast
Environment="INFLUXDB_TOKEN=your-token"
Environment="INFLUXDB_URL=http://localhost:8086"
ExecStart=/usr/bin/python3 api-service/api_enhanced.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable electricity-forecast-api
sudo systemctl start electricity-forecast-api

# Check status
sudo systemctl status electricity-forecast-api
```

## Support

If you continue to have issues:

1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Check API logs where you ran the API service
3. Create an issue on GitHub with:
   - Your URL configuration
   - Network setup (Docker, separate machines, etc.)
   - Error messages from logs
