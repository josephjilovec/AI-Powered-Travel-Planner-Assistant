# AI-Powered Travel Planner Assistant

A production-ready, enterprise-grade travel planning application powered by Google Gemini AI, optimized for deployment on Streamlit Cloud.

## 🌟 Features

- **Intelligent Preference Extraction**: AI analyzes natural language input to understand travel preferences, interests, and requirements
- **Smart Recommendations**: Personalized recommendations for attractions, accommodations, dining, and transportation
- **Detailed Itineraries**: Day-by-day travel itineraries that consider preferences, time constraints, and practical considerations
- **Dietary Awareness**: Considers dietary restrictions and preferences
- **Budget Consideration**: Takes budget into account when making recommendations
- **Professional UI**: Clean, modern interface with sidebar navigation and custom themes

## 🏗️ Architecture

The application follows a modular, enterprise-grade architecture:

```
AI-Powered-Travel-Planner-Assistant/
├── streamlit_app.py          # Main Streamlit entry point
├── config.py                 # Configuration management (st.secrets)
├── requirements.txt          # Python dependencies with exact versions
├── .streamlit/
│   └── config.toml          # Streamlit Cloud configuration
├── src/
│   ├── agents/              # AI agent implementations
│   │   ├── base_agent.py
│   │   ├── preference_agent.py
│   │   ├── search_agent.py
│   │   └── itinerary_agent.py
│   └── orchestrator.py      # Coordinates agent interactions
├── utils/                   # Utility modules
│   ├── logger.py           # Logging configuration
│   ├── api_client.py       # Gemini API client
│   └── validators.py       # Input validation
└── components/             # Streamlit UI components
    └── ui_components.py    # Reusable UI components
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- **Optional**: Google Cloud Project with Gemini API enabled and API key (for production)
- **For Demo**: No API key needed! See [DEMO_MODE.md](DEMO_MODE.md)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-travel-planner.git
   cd ai-travel-planner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (Optional)**
   
   **Option A: Demo Mode (No API key needed)**
   ```bash
   # Windows
   set DEMO_MODE=true
   
   # macOS/Linux
   export DEMO_MODE=true
   ```
   
   **Option B: Production Mode (Requires API key)**
   
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   
   Or set it as an environment variable:
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # macOS/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

   The application will open in your browser at `http://localhost:8501`

## ☁️ Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository

1. Push your code to a GitHub repository
2. Ensure `streamlit_app.py` is in the root directory
3. Ensure `requirements.txt` is in the root directory

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path to: `streamlit_app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

1. In your Streamlit Cloud app dashboard, go to "Settings" → "Secrets"
2. Choose one of the following:

   **Option A: Demo Mode (No API key needed - Perfect for showcasing!)**
   ```toml
   DEMO_MODE = "true"
   ```
   This enables demo mode with mock data. Perfect for demonstrating the UI without needing an API key.

   **Option B: Production Mode (Requires API key)**
   ```toml
   DEMO_MODE = "false"
   GEMINI_API_KEY = "your_api_key_here"
   ```
   
   Optional configuration:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   GEMINI_MODEL = "gemini-pro"
   MAX_RETRIES = "3"
   TIMEOUT = "30"
   ```

3. Click "Save" and the app will automatically redeploy

> 💡 **Tip**: Start with Demo Mode to showcase your app, then switch to production mode when ready!

## 📋 Configuration

### Environment Variables / Streamlit Secrets

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEMO_MODE` | Enable demo mode (uses mock data, no API key needed) | No | `false` (auto-enabled if no API key) |
| `GEMINI_API_KEY` | Google Gemini API key | Yes* | - |
| `GEMINI_MODEL` | Gemini model to use | No | `gemini-pro` |
| `MAX_RETRIES` | Maximum API retry attempts | No | `3` |
| `TIMEOUT` | API timeout in seconds | No | `30` |

*Required only if `DEMO_MODE` is `false` or not set and you want to use real AI features.

### Local Development

For local development, use a `.env` file or environment variables.

**Demo Mode Example:**
```bash
export DEMO_MODE=true
```

**Production Mode Example:**
```bash
export GEMINI_API_KEY=your_key_here
export DEMO_MODE=false
```

### Streamlit Cloud

For Streamlit Cloud deployment, use the Secrets management in the dashboard (see Deployment section above).

> 📖 **Learn more**: See [DEMO_MODE.md](DEMO_MODE.md) for detailed information about demo mode.

## 🧪 Testing

Run tests (when available):
```bash
pytest tests/
```

## 📝 Code Quality

The codebase follows enterprise standards:

- **PEP 8 compliant**: All code adheres to Python style guidelines
- **Type hints**: All functions include type annotations
- **Comprehensive logging**: Structured logging throughout the application
- **Error handling**: Robust try-except blocks with specific exceptions
- **Modular design**: Clean separation of concerns

## 🔧 Development

### Project Structure

- **`src/agents/`**: AI agent implementations using the Gemini API
- **`src/orchestrator.py`**: Coordinates the flow between agents
- **`utils/`**: Utility functions for logging, API clients, and validation
- **`components/`**: Reusable Streamlit UI components
- **`config.py`**: Centralized configuration management

### Adding New Features

1. Create new agent classes in `src/agents/` inheriting from `BaseAgent`
2. Add UI components in `components/ui_components.py`
3. Update the orchestrator in `src/orchestrator.py` if needed
4. Add validation logic in `utils/validators.py` if needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🐛 Troubleshooting

### API Key Issues

- Ensure your API key is correctly set in Streamlit secrets or environment variables
- Verify the API key has access to the Gemini API
- Check that billing is enabled on your Google Cloud project

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Python 3.9+ is being used
- Verify the project structure matches the expected layout

### Deployment Issues

- Ensure `streamlit_app.py` is in the root directory
- Verify `requirements.txt` includes all dependencies
- Check Streamlit Cloud logs for detailed error messages

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Cloud Deployment Guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)

