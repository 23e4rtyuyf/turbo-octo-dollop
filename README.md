# 🧠 AI Email Router

AI-powered email classification and routing engine. Automatically classify incoming emails using OpenAI and route them to the right team — support, sales, billing, spam — in real time.

## Features

- **AI Classification** — Uses OpenAI GPT to classify emails into categories: complaint, lead, billing, support, partnership, spam
- **Smart Routing** — Automatically routes classified emails to configured destinations
- **Multiple Integrations** — Slack, email forwarding, webhook (CRM, etc.)
- **Configurable Rules** — REST API to manage routing rules on the fly
- **Fast & Async** — Built on FastAPI with full async support
- **Docker Ready** — One command to run with Docker Compose

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/23e4rtyuyf/turbo-octo-dollop.git
cd turbo-octo-dollop
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API docs.

### 4. Test It

```bash
curl -X POST http://localhost:8000/api/v1/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "angry.customer@gmail.com",
    "recipient": "support@yourcompany.com",
    "subject": "THIS IS UNACCEPTABLE",
    "body_plain": "I have been waiting 3 weeks for my order and nobody is responding. I want a full refund immediately."
  }'
```

### Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/inbound` | Receive, classify, and route an email |
| POST | `/api/v1/classify` | Classify an email without routing |
| GET | `/api/v1/rules/` | List all routing rules |
| PUT | `/api/v1/rules/{category}` | Update a routing rule |
| DELETE | `/api/v1/rules/{category}` | Delete a custom rule |
| GET | `/api/v1/dashboard/stats` | Get email routing statistics |

## Architecture

```
Incoming Email → Webhook Receiver → AI Classifier → Routing Engine → Slack / Email / Webhook
```

## License

MIT
