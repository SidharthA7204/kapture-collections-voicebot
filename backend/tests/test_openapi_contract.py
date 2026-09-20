from fastapi.testclient import TestClient

from app.main import app


def test_vapi_webhook_has_response_schema_in_openapi():
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()

    webhook = openapi["paths"]["/vapi/webhook"]["post"]

    response_schema = webhook["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema["$ref"] == (
        "#/components/schemas/VapiWebhookResponse"
    )


def test_vapi_webhook_response_schema_is_defined():
    client = TestClient(app)

    openapi = client.get("/openapi.json").json()

    schemas = openapi["components"]["schemas"]

    assert "VapiWebhookResponse" in schemas

    schema = schemas["VapiWebhookResponse"]

    assert schema["properties"]["status"]["type"] == "string"
    assert schema["properties"]["event_type"]["type"] == "string"
    assert schema["properties"]["call_id"]["type"] == "string"
