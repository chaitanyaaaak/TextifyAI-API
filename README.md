# TextifyAI Backend

A high-performance FastAPI backend designed to orchestrate NLP tasks and Large Language Model (LLM) interactions for the TextifyAI suite.

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **LLM API**: OpenRouter (OpenAI-compatible SDK)
- **Local NLP**: SymSpell (for high-speed spelling correction)
- **Validation**: Pydantic v2
- **Server**: Uvicorn

## 📦 Features

- **Asynchronous LLM Integration**: Streamed AI responses using Server-Sent Events (SSE).
- **Professional Role Logic**: Domain-specific system prompting and context management.
- **Background Processing**: Asynchronous file analysis (PDF, CSV, TXT) with error reporting.
- **Medical Whitelist**: Built-in domain-specific whitelist to prevent false positives in medical documentation.

## 🚀 Getting Started

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file based on `.env.example`:
   ```env
   OPENROUTER_API_KEY=your_key_here
   LLM_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
   FRONTEND_URL=https://textify-ai-seven.vercel.app/
   ```

4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

## 🚀 Deployment (Render)

This project is configured for easy deployment on [Render](https://render.com).

1. **Connect Repository**: Connect your GitHub repository to Render.
2. **Setup Blueprints**: Render will automatically detect the `render.yaml` file.
3. **Environment Variables**:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key.
   - `FRONTEND_URL`: Set this to `https://textify-ai-seven.vercel.app/`.
4. **Service Type**: Web Service (Python).

## 📂 Project Structure

```text
├── app/
│   ├── api/v1/endpoints/  # API routes
│   ├── core/              # Global configuration
│   ├── data/              # Static data & whitelists
│   ├── models/            # Shared models
│   ├── schemas/           # Pydantic validation schemas
│   ├── services/          # Core business logic
│   └── main.py            # FastAPI entry point
├── tests/                 # Unit & integration tests
├── requirements.txt       # Production dependencies
├── render.yaml            # Deployment blueprint
└── README.md              # Documentation
```

## 📜 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

