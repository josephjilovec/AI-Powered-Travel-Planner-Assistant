# Deployment Guide for Streamlit Cloud

This guide provides step-by-step instructions for deploying the AI-Powered Travel Planner Assistant to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
3. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Ensure your repository structure matches the expected layout:
   ```
   AI-Powered-Travel-Planner-Assistant/
   ├── streamlit_app.py
   ├── requirements.txt
   ├── config.py
   ├── .streamlit/
   │   └── config.toml
   ├── src/
   ├── utils/
   └── components/
   ```

2. Verify that `streamlit_app.py` is in the root directory
3. Verify that `requirements.txt` includes all dependencies with exact versions

### Step 2: Push to GitHub

1. Commit all changes:
   ```bash
   git add .
   git commit -m "Production-ready refactoring for Streamlit Cloud"
   git push origin main
   ```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in the deployment form:
   - **Repository**: Select your repository
   - **Branch**: Select `main` (or your default branch)
   - **Main file path**: Enter `streamlit_app.py`
   - **App URL**: Choose a unique URL (optional)
5. Click **"Deploy"**

### Step 4: Configure Secrets

1. In your Streamlit Cloud app dashboard, click **"Settings"** (⚙️ icon)
2. Navigate to **"Secrets"** in the sidebar
3. Add your secrets in TOML format:

   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

   Optional configuration:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   GEMINI_MODEL = "gemini-pro"
   MAX_RETRIES = "3"
   TIMEOUT = "30"
   ```

4. Click **"Save"** - the app will automatically redeploy

### Step 5: Verify Deployment

1. Wait for the deployment to complete (usually 1-2 minutes)
2. Check the app logs for any errors:
   - Click **"Manage app"** → **"Logs"**
3. Open your app URL and test the functionality

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Symptom**: `ModuleNotFoundError` in logs

**Solution**:
- Verify all dependencies are in `requirements.txt`
- Check that package names and versions are correct
- Ensure Python 3.9+ is being used

#### 2. API Key Errors

**Symptom**: `ValueError: GEMINI_API_KEY is required`

**Solution**:
- Verify secrets are configured correctly in Streamlit Cloud
- Check that the secret name is exactly `GEMINI_API_KEY`
- Ensure there are no extra spaces or quotes in the secret value

#### 3. Deployment Fails

**Symptom**: App fails to start

**Solution**:
- Check the logs for specific error messages
- Verify `streamlit_app.py` is in the root directory
- Ensure all required files are committed to GitHub
- Check that `requirements.txt` has valid package versions

#### 4. Slow Performance

**Symptom**: App is slow to respond

**Solution**:
- The app uses caching (`@st.cache_resource` and `@st.cache_data`) to improve performance
- API calls to Gemini may take a few seconds - this is normal
- Consider adjusting cache TTL values if needed

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | `AIzaSy...` |
| `GEMINI_MODEL` | Model name to use | No | `gemini-pro` |
| `MAX_RETRIES` | API retry attempts | No | `3` |
| `TIMEOUT` | API timeout (seconds) | No | `30` |

## Updating Your App

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. Streamlit Cloud will automatically detect changes and redeploy
4. Monitor the deployment in the Streamlit Cloud dashboard

## Monitoring

- **Logs**: Access real-time logs in the Streamlit Cloud dashboard
- **Usage**: Monitor app usage and performance metrics
- **Errors**: Check logs for any runtime errors or exceptions

## Security Best Practices

1. **Never commit secrets**: Ensure `.env` files and secrets are in `.gitignore`
2. **Use Streamlit Secrets**: Always use Streamlit Cloud's secrets management, never hardcode API keys
3. **Rotate keys**: Regularly rotate your API keys for security
4. **Monitor usage**: Keep an eye on API usage to detect any anomalies

## Support

For issues or questions:
- Check the [Streamlit Cloud Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- Review the [README.md](README.md) for general information
- Check application logs for detailed error messages

