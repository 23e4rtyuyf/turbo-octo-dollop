from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.inbound import router as inbound_router
from app.api.rules import router as rules_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.billing import router as billing_router
from app.db.database import init_db
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered email classification and routing engine. Classify incoming emails and route them to the right team automatically.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inbound_router)
app.include_router(rules_router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(billing_router)


LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Email Router</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 60px 20px; }
        .hero { text-align: center; margin-bottom: 80px; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 20px; background: linear-gradient(to right, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.3rem; color: #b0b0cc; max-width: 600px; margin: 0 auto 30px; }
        .cta { display: inline-block; padding: 15px 40px; background: linear-gradient(to right, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 8px; font-size: 1.1rem; font-weight: 600; transition: transform 0.2s; }
        .cta:hover { transform: translateY(-2px); }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 80px; }
        .feature { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; }
        .feature h3 { font-size: 1.3rem; margin-bottom: 10px; color: #667eea; }
        .feature p { color: #9999bb; line-height: 1.6; }
        .pricing { text-align: center; margin-bottom: 80px; }
        .pricing h2 { font-size: 2.5rem; margin-bottom: 40px; }
        .plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .plan { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; text-align: center; }
        .plan.featured { border-color: #667eea; background: rgba(102,126,234,0.1); }
        .plan h3 { font-size: 1.5rem; margin-bottom: 10px; }
        .plan .price { font-size: 2.5rem; font-weight: 700; margin-bottom: 20px; }
        .plan .price span { font-size: 1rem; color: #9999bb; }
        .plan ul { list-style: none; margin-bottom: 20px; }
        .plan ul li { padding: 8px 0; color: #b0b0cc; }
        .plan ul li::before { content: "✓ "; color: #667eea; }
        footer { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🧠 AI Email Router</h1>
            <p>Automatically classify and route incoming emails to the right team using AI. Stop manually sorting through your inbox.</p>
            <a href="/docs" class="cta">Try the API →</a>
        </div>
        <div class="features">
            <div class="feature">
                <h3>🤖 AI Classification</h3>
                <p>GPT-powered email analysis classifies messages as complaints, leads, billing, support, partnerships, or spam with 95%+ accuracy.</p>
            </div>
            <div class="feature">
                <h3>⚡ Instant Routing</h3>
                <p>Emails are classified and routed in under 2 seconds. Connect Slack, email forwarding, webhooks, or any CRM.</p>
            </div>
            <div class="feature">
                <h3>📊 Analytics Dashboard</h3>
                <p>Track classification accuracy, volume by category, response times, and team performance in real-time.</p>
            </div>
            <div class="feature">
                <h3>🔌 Easy Integration</h3>
                <p>Works with SendGrid, Mailgun, AWS SES, Slack, HubSpot, Salesforce, and any webhook-compatible tool.</p>
            </div>
            <div class="feature">
                <h3>🔐 Enterprise Security</h3>
                <p>API key authentication, rate limiting, quota management, and full audit logging built in.</p>
            </div>
            <div class="feature">
                <h3>💰 Usage-Based Pricing</h3>
                <p>Start free with 100 emails/month. Scale to millions with transparent, predictable pricing.</p>
            </div>
        </div>
        <div class="pricing">
            <h2>Simple Pricing</h2>
            <div class="plans">
                <div class="plan">
                    <h3>Free</h3>
                    <div class="price">$0<span>/mo</span></div>
                    <ul>
                        <li>100 emails/month</li>
                        <li>Basic classification</li>
                        <li>Email routing</li>
                    </ul>
                </div>
                <div class="plan featured">
                    <h3>Pro</h3>
                    <div class="price">$49<span>/mo</span></div>
                    <ul>
                        <li>5,000 emails/month</li>
                        <li>Slack integration</li>
                        <li>Analytics dashboard</li>
                        <li>Custom routing rules</li>
                    </ul>
                </div>
                <div class="plan">
                    <h3>Business</h3>
                    <div class="price">$199<span>/mo</span></div>
                    <ul>
                        <li>50,000 emails/month</li>
                        <li>Webhook integrations</li>
                        <li>Full API access</li>
                        <li>Priority support</li>
                    </ul>
                </div>
                <div class="plan">
                    <h3>Enterprise</h3>
                    <div class="price">$999<span>/mo</span></div>
                    <ul>
                        <li>Unlimited emails</li>
                        <li>SSO / SAML</li>
                        <li>SLA guarantee</li>
                        <li>White-label option</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    <footer>
        <p>AI Email Router — Built with FastAPI + OpenAI</p>
    </footer>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return LANDING_PAGE_HTML


@app.get("/health")
async def health():
    return {"status": "healthy"}
