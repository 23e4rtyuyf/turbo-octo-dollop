import httpx
from app.config import settings


async def send_slack_message(channel: str, message: str) -> bool:
    """Send a message to a Slack channel."""
    if not settings.slack_bot_token:
        print(f"[SLACK DRY RUN] → {channel}: {message[:100]}...")
        return True

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.slack_bot_token}"},
            json={"channel": channel, "text": message},
        )
        data = response.json()
        if not data.get("ok"):
            print(f"[SLACK ERROR] {data.get('error')}")
            return False
        return True
