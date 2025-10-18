# Publishing Guide - Share Your Integration with the Community

This guide walks you through publishing your Home Assistant integration so others can use it.

## Overview

There are two main ways to publish:
1. **HACS (Home Assistant Community Store)** - Easiest for users to install
2. **GitHub Repository** - Manual installation, but works immediately

## Step 1: Create GitHub Repository

### 1.1 Create New Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click **New Repository** (or go to https://github.com/new)
3. Repository details:
   - **Name**: `electricity-forecast-ha` (or similar)
   - **Description**: "Home Assistant integration for electricity price forecasting with solar panel optimization"
   - **Public**: ✅ (required for HACS)
   - **Add README**: ❌ (we'll add our own)
   - **Add .gitignore**: ✅ Select "Python"
   - **License**: MIT License (recommended)

4. Click **Create Repository**

### 1.2 Clone Repository Locally

```bash
cd /workspaces/weather-forecast/homeassistant-integration
git init
git remote add origin https://github.com/YOUR-USERNAME/electricity-forecast-ha.git
```

### 1.3 Prepare Files for Publishing

```bash
# Copy integration files
mkdir -p electricity-forecast-ha
cp -r custom_components electricity-forecast-ha/
cp README.md electricity-forecast-ha/
cp INSTALLATION_GUIDE.md electricity-forecast-ha/
cp hacs.json electricity-forecast-ha/
cp -r .github electricity-forecast-ha/

cd electricity-forecast-ha
```

### 1.4 Update manifest.json

Edit `custom_components/electricity_forecast/manifest.json` and update:
- `codeowners`: Your GitHub username
- `documentation`: Your repository URL
- `issue_tracker`: Your repository issues URL

```json
{
  "domain": "electricity_forecast",
  "name": "Electricity Price Forecast",
  "codeowners": ["@YOUR-GITHUB-USERNAME"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/YOUR-USERNAME/electricity-forecast-ha",
  "integration_type": "hub",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/YOUR-USERNAME/electricity-forecast-ha/issues",
  "requirements": [],
  "version": "1.0.0"
}
```

### 1.5 Update README.md

Replace all instances of `YOUR-USERNAME` with your actual GitHub username.

### 1.6 Commit and Push

```bash
git add .
git commit -m "Initial commit - Electricity Price Forecast integration v1.0.0"
git branch -M main
git push -u origin main
```

## Step 2: Create First Release

### 2.1 Tag Version

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Initial release

Features:
- 8 sensor entities for price tracking
- Smart recommendations for battery charging
- Support for all 8 German regions
- 24h and 7-day forecasts
- Configuration flow for easy setup
"

git push origin v1.0.0
```

### 2.2 Create GitHub Release

1. Go to your repository on GitHub
2. Click **Releases** (right sidebar)
3. Click **Create a new release**
4. Fill in:
   - **Tag**: Select `v1.0.0`
   - **Title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```markdown
     ## 🎉 Initial Release

     Home Assistant integration for electricity price forecasting, optimized for solar panel battery management.

     ### ✨ Features
     - 8 sensor entities tracking prices and trends
     - Smart recommendations (charge/discharge/hold)
     - Support for all 8 German regions
     - 24-hour and 7-day forecasts
     - Easy configuration through UI
     - Full forecast data as sensor attributes

     ### 📊 Sensors
     - Current Price
     - Next Hour Price
     - Average Price Today
     - Cheapest Hour Today
     - Most Expensive Hour Today
     - Price Trend (rising/falling/stable)
     - Recommendation (charge/discharge/neutral)
     - Forecast (full 24h/7d data)

     ### 🔧 Installation
     See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions.

     ### 📖 Documentation
     - [README.md](README.md) - Full documentation
     - [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Step-by-step setup

     ### 🐛 Known Issues
     None yet! Please report any issues you find.

     ### 🙏 Credits
     Developed for the Home Assistant community.
     ```

5. Click **Publish release**

## Step 3: Submit to HACS

### 3.1 Verify HACS Requirements

Your repository must have:
- ✅ Public repository
- ✅ `hacs.json` file in root
- ✅ `custom_components/electricity_forecast/` directory
- ✅ `manifest.json` with all required fields
- ✅ At least one release (v1.0.0)
- ✅ README.md with documentation
- ✅ GitHub Actions workflow for validation

### 3.2 Test HACS Validation Locally

```bash
# Install HACS action tool
pip install hacs-validate

# Run validation
hacs-validate --repository electricity-forecast-ha
```

### 3.3 Submit to HACS Default Repository

1. Fork the [HACS default repository](https://github.com/hacs/default)

   ```bash
   # Visit: https://github.com/hacs/default
   # Click "Fork" button
   ```

2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/default.git hacs-default
   cd hacs-default
   ```

3. Create a new branch:

   ```bash
   git checkout -b add-electricity-forecast
   ```

4. Edit `custom_components.json` and add your integration:

   ```json
   {
     "YOUR-USERNAME/electricity-forecast-ha": {
       "name": "Electricity Price Forecast",
       "domains": ["sensor"],
       "iot_class": "cloud_polling",
       "render_readme": true
     }
   }
   ```

   Add it alphabetically in the file.

5. Commit and push:

   ```bash
   git add custom_components.json
   git commit -m "Add Electricity Price Forecast integration"
   git push origin add-electricity-forecast
   ```

6. Create Pull Request:
   - Go to https://github.com/hacs/default
   - Click "Pull requests"
   - Click "New pull request"
   - Click "compare across forks"
   - Select your fork and branch
   - Title: "Add Electricity Price Forecast"
   - Description:
     ```markdown
     ## Description
     Home Assistant integration for electricity price forecasting and solar panel battery optimization.

     ## Checklist
     - [x] Repository is public
     - [x] Has at least one release
     - [x] Has hacs.json
     - [x] Has valid manifest.json
     - [x] Has documentation
     - [x] Passes HACS validation

     ## Repository
     https://github.com/YOUR-USERNAME/electricity-forecast-ha

     ## Features
     - Real-time electricity price tracking
     - Smart charging recommendations
     - Support for 8 German regions
     - 24h/7d forecasts
     ```

7. Wait for HACS team review (usually 1-3 days)

### 3.4 Alternative: Add as Custom Repository (Faster)

While waiting for HACS approval, users can add as custom repository:

Add to your README:

```markdown
### Installation via HACS (Custom Repository)

1. Open HACS → Integrations
2. Click ⋮ (three dots) → Custom repositories
3. Add repository: `https://github.com/YOUR-USERNAME/electricity-forecast-ha`
4. Category: Integration
5. Click "Add"
6. Find "Electricity Price Forecast" and install
```

## Step 4: Promote Your Integration

### 4.1 Home Assistant Community Forum

1. Go to https://community.home-assistant.io/
2. Category: "Share your Projects"
3. Create post:

   **Title**: "Electricity Price Forecast - Optimize Solar Battery Charging"

   **Content**:
   ```markdown
   I've created a Home Assistant integration for electricity price forecasting, specifically designed for solar panel owners to optimize battery charging.

   ## Features
   - Real-time price tracking for German regions
   - Smart recommendations: when to charge, discharge, or hold
   - 8 sensors tracking prices, trends, and forecasts
   - Easy automation for battery management
   - 24-hour and 7-day forecasts

   ## Use Cases
   - Charge batteries during cheapest hours
   - Sell to grid during expensive hours
   - Schedule appliances (dishwasher, EV charging) optimally
   - Maximize solar ROI

   ## Screenshots
   [Add dashboard screenshots here]

   ## Installation
   Available via HACS or manual installation.

   GitHub: https://github.com/YOUR-USERNAME/electricity-forecast-ha
   Documentation: [Link to README]

   ## Feedback Welcome!
   This is my first Home Assistant integration. Please try it out and let me know what you think!
   ```

### 4.2 Reddit

Post to r/homeassistant:

**Title**: "New Integration: Electricity Price Forecast for Solar Battery Optimization"

**Content**: Similar to forum post, but shorter. Add screenshots!

### 4.3 Create Demo Video (Optional but Recommended)

Record a short video (5-10 minutes) showing:
1. Installation process
2. Configuration
3. Dashboard with sensors
4. Example automation (battery charging)
5. Explanation of use cases

Upload to YouTube and link in README.

### 4.4 Add Screenshots to README

Take screenshots of:
- Configuration dialog
- Sensors in Developer Tools
- Example dashboard
- Price chart (if using ApexCharts)
- Automation examples

Add to README:

```markdown
## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Configuration
![Config](screenshots/config.png)

### Sensors
![Sensors](screenshots/sensors.png)
```

## Step 5: Maintain Your Integration

### 5.1 Handle Issues

- Monitor GitHub issues
- Respond within 48 hours (even if just to acknowledge)
- Label issues (bug, enhancement, question)
- Close fixed issues with release notes

### 5.2 Release Updates

When making changes:

```bash
# Update version in manifest.json
# "version": "1.1.0"

# Commit changes
git add .
git commit -m "feat: Add new feature X"

# Tag new version
git tag -a v1.1.0 -m "Release v1.1.0

- Added feature X
- Fixed bug Y
- Improved performance Z
"

git push origin main
git push origin v1.1.0

# Create GitHub release
```

### 5.3 Semantic Versioning

Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR** (2.0.0): Breaking changes
- **MINOR** (1.1.0): New features, backwards compatible
- **PATCH** (1.0.1): Bug fixes

### 5.4 Changelog

Keep a CHANGELOG.md:

```markdown
# Changelog

## [1.1.0] - 2025-11-01
### Added
- New sensor for peak/off-peak classification
- Support for dynamic tariffs

### Fixed
- Connection timeout when API is slow

## [1.0.0] - 2025-10-17
### Added
- Initial release
- 8 sensor entities
- Support for 8 German regions
```

## Step 6: Advanced Publishing

### 6.1 Add Brand Images

Create `custom_components/electricity_forecast/` folder with:
- `icon.png` - 256x256px integration icon
- `logo.png` - 512x128px brand logo

### 6.2 Add More Translations

Create `translations/de.json` for German users:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Strompreisprognose konfigurieren",
        "description": "Richten Sie Ihre Strompreisprognose-Integration ein.",
        "data": {
          "api_url": "API-URL",
          "region_id": "Region"
        }
      }
    }
  }
}
```

### 6.3 Add Tests

Create `tests/` directory with unit tests:

```python
# tests/test_sensor.py
"""Test electricity_forecast sensors."""
import pytest
from custom_components.electricity_forecast.sensor import CurrentPriceSensor

def test_current_price_sensor():
    """Test current price sensor."""
    # Add test implementation
    pass
```

### 6.4 Code Coverage

Add to GitHub Actions:

```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=custom_components.electricity_forecast --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Step 7: Marketing & Growth

### 7.1 Create Documentation Website

Use GitHub Pages:

```bash
# Create docs/ folder
mkdir docs
cd docs

# Create index.html with documentation
# Push to GitHub

# Enable GitHub Pages:
# Settings → Pages → Source: main branch /docs folder
```

### 7.2 Create Logo & Banner

Use Canva or similar to create:
- Integration logo
- Repository banner image
- Social media preview image

### 7.3 Add Badges to README

```markdown
[![GitHub Release](https://img.shields.io/github/release/YOUR-USERNAME/electricity-forecast-ha.svg)](https://github.com/YOUR-USERNAME/electricity-forecast-ha/releases)
[![GitHub Downloads](https://img.shields.io/github/downloads/YOUR-USERNAME/electricity-forecast-ha/total.svg)](https://github.com/YOUR-USERNAME/electricity-forecast-ha/releases)
[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/YOUR-USERNAME/electricity-forecast-ha.svg)](LICENSE)
```

### 7.4 Get Feedback Early

Before v1.0.0:
1. Share with friends who use Home Assistant
2. Post as "beta" in community forum
3. Iterate based on feedback
4. Then do official v1.0.0 release

## Checklist Before Publishing

- [ ] All `YOUR-USERNAME` placeholders replaced
- [ ] manifest.json has correct URLs
- [ ] README.md is complete with examples
- [ ] INSTALLATION_GUIDE.md is clear
- [ ] At least one GitHub release created
- [ ] GitHub Actions validation passes
- [ ] hacs.json is valid
- [ ] Integration works on test Home Assistant instance
- [ ] Screenshots added to README
- [ ] License file included (MIT recommended)
- [ ] Code is well-commented
- [ ] No sensitive data (tokens, passwords) in code

## Success Metrics

Track your integration's adoption:
- GitHub stars
- HACS installs (if accepted)
- GitHub issues (engagement)
- Community forum mentions
- YouTube views (if you made video)

## Support Your Users

- Respond to issues promptly
- Accept pull requests for improvements
- Keep documentation updated
- Release fixes quickly
- Thank contributors

## Need Help?

- Home Assistant Developer Docs: https://developers.home-assistant.io/
- HACS Documentation: https://hacs.xyz/docs/publish/integration
- Home Assistant Discord: https://discord.gg/home-assistant

Good luck with your integration! 🚀
