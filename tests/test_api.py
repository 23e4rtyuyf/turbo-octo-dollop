import pytest
from fastapi.testclient import TestClient


class TestHealthAndLanding:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_landing_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "AI Email Router" in response.text
        assert "text/html" in response.headers["content-type"]

    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200


class TestClassification:
    def test_classify_email_no_api_key(self, client):
        """Without an API key configured, should return 'other' category."""
        email_payload = {
            "sender": "test@example.com",
            "recipient": "support@company.com",
            "subject": "Test email",
            "body_plain": "This is a test email body.",
        }
        response = client.post("/api/v1/classify", json=email_payload)
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "confidence" in data
        assert "reasoning" in data
        assert data["sender"] == "test@example.com"

    def test_classify_missing_fields(self, client):
        response = client.post("/api/v1/classify", json={"sender": "test@example.com"})
        assert response.status_code == 422

    def test_inbound_email_logs_to_db(self, client):
        """Test that inbound emails are logged to the database."""
        email_payload = {
            "sender": "customer@example.com",
            "recipient": "support@company.com",
            "subject": "Help needed",
            "body_plain": "I need help with my account.",
        }
        response = client.post("/api/v1/inbound", json=email_payload)
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "routed_to" in data


class TestRoutingRules:
    def test_list_rules_empty(self, client):
        response = client.get("/api/v1/rules/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_rule(self, client):
        rule = {
            "category": "complaint",
            "destination_type": "email",
            "destination_target": "complaints@company.com",
            "enabled": True,
        }
        response = client.post("/api/v1/rules/", json=rule)
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "complaint"
        assert data["destination_type"] == "email"
        assert data["id"] is not None

    def test_create_duplicate_rule(self, client):
        rule = {
            "category": "lead",
            "destination_type": "email",
            "destination_target": "sales@company.com",
        }
        client.post("/api/v1/rules/", json=rule)
        response = client.post("/api/v1/rules/", json=rule)
        assert response.status_code == 400

    def test_update_rule(self, client):
        rule = {
            "category": "support",
            "destination_type": "email",
            "destination_target": "support@company.com",
        }
        create_resp = client.post("/api/v1/rules/", json=rule)
        rule_id = create_resp.json()["id"]

        updated_rule = {
            "category": "support",
            "destination_type": "slack",
            "destination_target": "#support-channel",
            "enabled": True,
        }
        response = client.put(f"/api/v1/rules/{rule_id}", json=updated_rule)
        assert response.status_code == 200
        assert response.json()["destination_type"] == "slack"

    def test_delete_rule(self, client):
        rule = {
            "category": "spam",
            "destination_type": "discard",
            "destination_target": "null",
        }
        create_resp = client.post("/api/v1/rules/", json=rule)
        rule_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/rules/{rule_id}")
        assert response.status_code == 200

        list_resp = client.get("/api/v1/rules/")
        assert all(r["id"] != rule_id for r in list_resp.json())

    def test_delete_nonexistent_rule(self, client):
        response = client.delete("/api/v1/rules/99999")
        assert response.status_code == 404


class TestDashboard:
    def test_get_stats_empty(self, client):
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 0
        assert data["by_category"] == {}
        assert "avg_confidence" in data

    def test_get_usage_no_org(self, client):
        response = client.get("/api/v1/dashboard/usage")
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "free"
        assert data["email_quota"] == 100

    def test_stats_after_emails(self, client):
        """Stats should reflect processed emails."""
        email_payload = {
            "sender": "test@example.com",
            "recipient": "inbox@company.com",
            "subject": "Test subject",
            "body_plain": "Test body",
        }
        client.post("/api/v1/inbound", json=email_payload)

        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 1


class TestAuthEndpoints:
    def test_generate_api_key(self, client):
        response = client.post("/api/v1/auth/api-key?name=test-key&org_id=testorg")
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("air_")
        assert "Save this key" in data["message"]

    def test_list_api_keys(self, client):
        client.post("/api/v1/auth/api-key?name=key1&org_id=myorg")
        client.post("/api/v1/auth/api-key?name=key2&org_id=myorg")

        response = client.get("/api/v1/auth/api-keys?org_id=myorg")
        assert response.status_code == 200
        keys = response.json()
        assert len(keys) == 2
        # Keys should be masked
        for k in keys:
            assert k["key_preview"].endswith("...")

    def test_revoke_api_key(self, client):
        create_resp = client.post("/api/v1/auth/api-key?name=to-revoke&org_id=testorg")
        # Generate a key and check it
        response = client.get("/api/v1/auth/api-keys?org_id=testorg")
        key_id = response.json()[0]["id"]

        revoke_resp = client.delete(f"/api/v1/auth/api-key/{key_id}")
        assert revoke_resp.status_code == 200

        # Confirm it's revoked
        response = client.get("/api/v1/auth/api-keys?org_id=testorg")
        assert response.json()[0]["is_active"] is False

    def test_revoke_nonexistent_key(self, client):
        response = client.delete("/api/v1/auth/api-key/99999")
        assert response.status_code == 404


class TestBillingPlans:
    def test_list_plans(self, client):
        response = client.get("/api/v1/billing/plans")
        assert response.status_code == 200
        data = response.json()
        assert "free" in data
        assert "pro" in data
        assert "business" in data
        assert "enterprise" in data

    def test_free_plan_details(self, client):
        response = client.get("/api/v1/billing/plans")
        free_plan = response.json()["free"]
        assert free_plan["price_cents"] == 0
        assert free_plan["email_quota"] == 100

    def test_checkout_invalid_plan(self, client):
        response = client.post("/api/v1/billing/checkout?plan=nonexistent")
        assert response.status_code == 400

    def test_checkout_free_plan_fails(self, client):
        response = client.post("/api/v1/billing/checkout?plan=free")
        assert response.status_code == 400
