# Demo Mode Guide

## Overview

The AI-Powered Travel Planner Assistant includes a **Demo Mode** that allows you to deploy and showcase the application without requiring a Google Gemini API key. This is perfect for:

- 🎭 Demonstrating the UI and user experience
- 🚀 Quick deployment to Streamlit Cloud
- 📱 Testing the application workflow
- 🎨 Showcasing the design and features

## How Demo Mode Works

When Demo Mode is enabled, the application uses **mock/sample data** instead of making real API calls to Google Gemini. The mock data is intelligent and adapts based on user input, providing realistic-looking results.

### Features in Demo Mode

- ✅ Full UI functionality
- ✅ Preference extraction (keyword-based)
- ✅ Travel recommendations (sample data)
- ✅ Detailed itineraries (generated templates)
- ✅ All navigation and features work normally

## Enabling Demo Mode

### Option 1: Streamlit Cloud Secrets (Recommended)

1. Go to your Streamlit Cloud app dashboard
2. Navigate to **Settings** → **Secrets**
3. Add the following:

```toml
DEMO_MODE = "true"
```

That's it! No API key needed. The app will automatically use demo data.

### Option 2: Environment Variable (Local Development)

Set the environment variable:

```bash
# Windows
set DEMO_MODE=true

# macOS/Linux
export DEMO_MODE=true
```

### Option 3: Automatic Detection

If no API key is found and `DEMO_MODE` is not explicitly set, the app will automatically enable demo mode.

## Disabling Demo Mode (Using Real API)

To use real AI features, you need to:

1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set it in Streamlit Cloud secrets:

```toml
DEMO_MODE = "false"
GEMINI_API_KEY = "your_actual_api_key_here"
```

Or for local development:

```bash
export DEMO_MODE=false
export GEMINI_API_KEY=your_actual_api_key_here
```

## Demo Mode Indicators

When running in Demo Mode, you'll see:

- 🎭 A banner at the top indicating "DEMO MODE"
- Mock data that adapts to your input
- Sample recommendations and itineraries

## Mock Data Behavior

The demo mode intelligently generates data based on your input:

- **Preferences**: Extracted from keywords in your description
- **Recommendations**: Sample recommendations for any destination
- **Itineraries**: Day-by-day templates that adapt to trip duration

### Example

If you enter:
- Destination: "Paris"
- Preferences: "I love museums and fine dining"
- Duration: 5 days

Demo mode will generate:
- Preferences with "Museums" and "Food & Dining" interests
- Recommendations including museum visits and restaurant suggestions
- A 5-day itinerary with museum visits and dining experiences

## Limitations in Demo Mode

- ⚠️ Data is not real-time or AI-generated
- ⚠️ Recommendations are generic templates
- ⚠️ Itineraries follow standard patterns
- ⚠️ No actual travel research or current information

## Best Practices

1. **For Showcasing**: Use Demo Mode to show the UI and workflow
2. **For Production**: Disable Demo Mode and use a real API key
3. **For Testing**: Demo Mode is great for testing the application flow
4. **For Development**: Use Demo Mode during development to avoid API costs

## Troubleshooting

### Demo Mode Not Working

- Check that `DEMO_MODE = "true"` is set in secrets
- Verify no valid API key is configured (or set a placeholder)
- Check application logs for mode detection

### Want to Switch to Real API

- Set `DEMO_MODE = "false"` in secrets
- Add a valid `GEMINI_API_KEY`
- The app will automatically switch to real API mode

## Security Note

Demo Mode is safe to use publicly - it doesn't require or use any API keys. The mock data is generated locally and doesn't make external API calls.

