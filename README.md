# DailyPulse Telegram Bot

DailyPulse is a Python-based Telegram chatbot integrated with OpenAI and automated workflows using n8n.  
The bot responds to user messages and logs all interactions into Google Sheets in real time.

## 🚀 Features
- Telegram bot built with **Python & aiogram**
- AI-powered responses using **OpenAI API**
- Automation via **n8n**
- Logs user messages & bot replies to **Google Sheets**
- Deployed on a VPS (24/7 running via tmux)

## 🧱 Tech Stack
- Python
- aiogram
- OpenAI API
- n8n
- Google Sheets API
- pytest, ruff, uv

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/dailypulse.git
cd dailypulse
## 🧪 Code Quality & Tests

This project includes basic Python tooling for code quality and testing.

### Tools used
- `pytest` – for running tests
- `ruff` – for linting and code style checks
- `uv` – for fast Python package management

### Commands
```bash
pip install pytest ruff uv
pytest
ruff check .

