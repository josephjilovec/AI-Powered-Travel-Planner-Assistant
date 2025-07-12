Contributing to AI-Powered Travel Planner Assistant
We warmly welcome contributions to the AI-Powered Travel Planner Assistant project! Your efforts, whether in reporting bugs, suggesting enhancements, or contributing code, are highly valued and help us build a better tool. Please review this document to understand our contribution process and guidelines.

Table of Contents
Code of Conduct

How Can I Contribute?

Reporting Bugs

Suggesting Enhancements

Contributing Code

Setting Up Your Development Environment

Prerequisites

Cloning the Repository

Virtual Environment Setup (Backend)

Installing Backend Dependencies

Frontend Setup

Configuring Environment (API Keys)

Running the Application Locally

Project Architecture Overview

Agents Layer (The Brains)

Applications Layer (The Interface & Orchestrator)

Proposing Changes and Submitting Pull Requests

Branching Strategy

Commit Messages

Creating a Pull Request

Coding Style Guidelines

Testing

License

Code of Conduct
Please note that this project adheres to a Contributor Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [your-email@example.com].

How Can I Contribute?
Reporting Bugs
If you find a bug, please open an issue on our GitHub Issues page. When reporting, please include:

A clear and concise description of the bug.

Steps to reproduce the behavior.

Expected behavior.

Screenshots or error messages, if applicable.

Your operating system, browser, Python version, and relevant library versions.

Suggesting Enhancements
Have an idea for a new feature or an improvement? Please open an issue on our GitHub Issues page with the label enhancement. Describe your idea clearly and explain its benefits.

Contributing Code
If you'd like to contribute code, please follow the steps outlined in the Setting Up Your Development Environment and Proposing Changes and Submitting Pull Requests sections.

Setting Up Your Development Environment
Prerequisites
Python 3.9+: Download and install from python.org.

Git: Download and install from git-scm.com.

Google Cloud Project & Gemini API Key: You'll need a Google Cloud Project with the Gemini API enabled and an associated API key.

Cloning the Repository
First, clone the repository to your local machine:

git clone https://github.com/your-username/ai-travel-planner.git
cd ai-travel-planner

(Note: Replace your-username with your actual GitHub username and ensure the repository name is correct.)

Virtual Environment Setup (Backend)
It is highly recommended to use a virtual environment for the Python backend to manage dependencies.

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

Installing Backend Dependencies
Once your virtual environment is active, install the required Python packages for the backend:

pip install -r requirements.txt

Frontend Setup
The frontend consists of HTML, CSS (Tailwind CSS via CDN), and plain JavaScript. No separate npm install is typically required for the frontend itself unless you introduce a build step (e.g., for bundling JS).

Configuring Environment (API Keys)
You will need to set up environment variables for the Google Gemini API key.

Create a file named .env in the root directory of the project.

Add your Google Gemini API key to this file:

GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY

Never commit your .env file to Git. It is already listed in .gitignore.

Running the Application Locally
Start the Flask Backend:
Ensure your virtual environment is active. From the project root directory:

python src/app.py

The Flask server will typically start on http://127.0.0.1:5000.

Access the Frontend:
Open your web browser and navigate to http://127.0.0.1:5000. The Flask application serves the index.html file.

Project Architecture Overview
The project is structured into two main conceptual layers:

Agents Layer (The Brains)
Located primarily in src/agents/, this layer contains the core AI logic, decision-making, reasoning, and simulated interaction with external tools. Each "agent" is a specialized AI persona (e.g., Preference Agent, Search Agent, Itinerary Agent) that leverages the Google Gemini API to perform its specific tasks.

Applications Layer (The Interface & Orchestrator)
This layer handles user interaction and overall application flow.

Backend (Flask): src/app.py defines API endpoints, manages state, and orchestrates calls to the Agents Layer.

Frontend (HTML/CSS/JavaScript): public/ directory contains the user-facing web interface, handling UI rendering, user input, and displaying results.

Proposing Changes and Submitting Pull Requests
Branching Strategy
We use a feature-branch workflow. Please create a new branch for each feature or bug fix you are working on.

# Update your local main branch
git checkout main
git pull origin main

# Create a new branch
git checkout -b feature/your-feature-name # for new features
# or
git checkout -b bugfix/your-bug-fix-name # for bug fixes

Commit Messages
Please write clear, concise, and descriptive commit messages. A good commit message explains what was changed and why.

Use the present tense ("Add feature" instead of "Added feature").

Use the imperative mood ("Fix bug" instead of "Fixes bug").

Limit the first line to 72 characters or less.

Reference relevant issue numbers if applicable (e.g., Fix #123).

Creating a Pull Request
Fork the repository on GitHub.

Clone your forked repository to your local machine.

Create a new branch for your changes (see Branching Strategy).

Make your changes and commit them with descriptive commit messages.

Run tests to ensure your changes haven't introduced regressions (see Testing).

Push your branch to your forked repository on GitHub.

git push origin feature/your-feature-name

Open a Pull Request from your forked repository to the main branch of the original ai-travel-planner repository.

Provide a clear title and detailed description for your pull request.

Explain the problem your PR solves or the feature it adds.

Reference any related issues (e.g., Closes #123).

Ensure your code adheres to the Coding Style Guidelines.

Coding Style Guidelines
Python: Adhere to PEP 8 for code style. Use Black for formatting and flake8 for linting.

JavaScript: Follow modern ES6+ best practices.

HTML/CSS: Use semantic HTML5 and follow Tailwind CSS conventions.

Testing
All new features and bug fixes should be accompanied by appropriate tests.

Unit Tests: For individual functions and classes (especially within the Agents Layer).

Integration Tests: For interactions between agents, and between the Applications Layer and Agents Layer.

To run the test suite (assuming pytest is installed):

pytest tests/

License
By contributing to AI-Powered Travel Planner Assistant, you agree that your contributions will be licensed under the MIT License.
