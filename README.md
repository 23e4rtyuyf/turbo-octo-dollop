# 🧠 AI Email Router

> **Automatically classify and route incoming emails to the right team using AI. Stop manually sorting through your inbox.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat&logo=python)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 What It Does

AI Email Router is a production-ready API service that:

1. **Receives** inbound emails via HTTP POST
2. **Classifies** them using GPT-4o-mini into 7 categories
3. **Routes** them to the right team (email, Slack, webhook, or CRM)
4. **Logs** everything to a database for analytics and auditing
5. **Bills** customers based on usage with Stripe integration

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Classification** | GPT-4o-mini classifies emails as complaint, lead, billing, support, partnership, spam, or other |
| ⚡ **Instant Routing** | Sub-2-second routing to email, Slack channels, webhooks, or discard |
| 📊 **Analytics Dashboard** | Real-time stats on volume, category breakdown, and confidence scores |
| 🔑 **API Key Auth** | Secure API key management per organization |
| 🏢 **Multi-tenant** | Organization-level isolation for all data and rules |
| 💳 **Stripe Billing** | Usage-based pricing with automatic quota enforcement |
| 🗄️ **SQLite/SQLAlchemy** | Persistent storage, zero configuration required |
| 🌐 **CORS Ready** | Full CORS support for web integrations |

---

## 🏗️ Architecture

```
┌─────────────────┐     POST /api/v1/inbound
│  Email Provider │ ──────────────────────────────┐
│ (SendGrid, SES) │                               ▼
└─────────────────┘                    ┌─────────────────────┐
                                       │   FastAPI App       │
┌─────────────────┐                    │                     │
│  Webhook Source │ ──────────────────▶│  1. Validate Input  │
└─────────────────┘                    │  2. AI Classify     │
                                       │  3. Route Email     │
                                       │  4. Log to DB       │
                                       └─────────┬───────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                        ┌──────────┐      ┌──────────┐      ┌──────────┐
                        │  Email   │      │  Slack   │      │ Webhook  │
                        │ Forward  │      │ Channel  │      │   URL    │
                        └──────────┘      └──────────┘      └──────────┘
```

---

## 📡 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/inbound` | Receive, classify, and route an email |
| `POST` | `/api/v1/classify` | Classify an email without routing (testing) |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |

### Rules Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/rules/` | List all routing rules |
| `POST` | `/api/v1/rules/` | Create a routing rule |
| `PUT` | `/api/v1/rules/{id}` | Update a routing rule |
| `DELETE` | `/api/v1/rules/{id}` | Delete a routing rule |

### Analytics Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/dashboard/stats` | Email stats for the last N days |
| `GET` | `/api/v1/dashboard/usage` | Current billing period usage |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/api-key` | Generate a new API key |
| `GET` | `/api/v1/auth/api-keys` | List API keys (masked) |
| `DELETE` | `/api/v1/auth/api-key/{id}` | Revoke an API key |

### Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/billing/plans` | List all pricing plans |
| `POST` | `/api/v1/billing/checkout` | Create Stripe checkout session |
| `POST` | `/api/v1/billing/webhook` | Handle Stripe webhook events |

---

## 💰 Pricing

| Plan | Price | Email Quota | Key Features |
|------|-------|-------------|--------------|
| **Free** | $0/mo | 100/mo | Basic classification, email routing |
| **Pro** | $49/mo | 5,000/mo | + Slack, analytics, custom rules |
| **Business** | $199/mo | 50,000/mo | + Webhooks, API access, priority support |
| **Enterprise** | $999/mo | Unlimited | + SSO/SAML, SLA, white-label |

---

## 🚀 Deploy on Replit (Easiest)

1. **Import the repository** — Go to [replit.com](https://replit.com), click **Create Repl** → **Import from GitHub**, paste this repo URL
2. **Add secrets** — In the Replit sidebar, go to **Secrets** and add:
   - `OPENAI_API_KEY` → Your OpenAI API key (required)
   - `STRIPE_SECRET_KEY` → Your Stripe secret key (optional, for billing)
   - `STRIPE_WEBHOOK_SECRET` → Your Stripe webhook secret (optional)
3. **Click Run** — Replit will install dependencies and start the server
4. **Visit your app** — The landing page will appear at your Replit URL

> **That's it!** The app auto-creates the SQLite database on first run.

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- An OpenAI API key

### Setup

```bash
# Clone the repository
git clone https://github.com/23e4rtyuyf/turbo-octo-dollop.git
cd turbo-octo-dollop

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 for the landing page and http://localhost:8000/docs for the API docs.

### Quick Test

```bash
# Classify a test email (no API key needed for /classify)
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "angry.customer@example.com",
    "recipient": "support@mycompany.com",
    "subject": "Your service is broken!!!",
    "body_plain": "I have been waiting 3 days for a response and nobody has helped me. This is unacceptable!"
  }'
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t ai-email-router .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e DATABASE_URL=sqlite:///./email_router.db \
  ai-email-router
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | — | OpenAI API key for classification |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `DATABASE_URL` | No | `sqlite:///./email_router.db` | SQLAlchemy database URL |
| `SLACK_BOT_TOKEN` | No | — | Slack bot token for Slack routing |
| `DEFAULT_FORWARD_EMAIL` | No | — | Fallback email for routing |
| `API_SECRET_KEY` | No | `change-me-in-production` | JWT/session secret |
| `STRIPE_SECRET_KEY` | No | — | Stripe secret key for billing |
| `STRIPE_WEBHOOK_SECRET` | No | — | Stripe webhook signing secret |
| `STRIPE_PUBLISHABLE_KEY` | No | — | Stripe publishable key |
| `DEBUG` | No | `false` | Enable debug mode |

---

## 🔌 Integration Examples

### SendGrid Inbound Parse Webhook

Point SendGrid's Inbound Parse to `https://your-app.repl.co/api/v1/inbound` and it will automatically classify and route all incoming emails.

### Mailgun Routes

```
Filter expression: catch_all()
Action: forward("https://your-app.repl.co/api/v1/inbound")
```

### Slack Routing Rule

```bash
curl -X POST http://localhost:8000/api/v1/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "category": "lead",
    "destination_type": "slack",
    "destination_target": "#sales-leads"
  }'
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ using FastAPI + OpenAI + SQLAlchemy*
