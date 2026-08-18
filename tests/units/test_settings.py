from canarytokens.settings import FrontendSettings


def test_frontend_settings_parse_comma_separated_environment_values(monkeypatch):
    monkeypatch.setenv("CANARY_PUBLIC_IP", "127.0.0.1")
    monkeypatch.setenv("CANARY_DOMAINS", "one.example,two.example")
    monkeypatch.setenv("CANARY_NXDOMAINS", "nx-one.example,nx-two.example")
    monkeypatch.setenv(
        "CANARY_MCP_SERVER_URLS", "https://one.example,https://two.example"
    )
    monkeypatch.setenv(
        "CANARY_DEFAULT_GUARDRAIL_TRIGGERS", "first trigger, , second trigger"
    )

    settings = FrontendSettings(_env_file=None)

    assert settings.DOMAINS == ["one.example", "two.example"]
    assert settings.NXDOMAINS == ["nx-one.example", "nx-two.example"]
    assert settings.MCP_SERVER_URLS == [
        "https://one.example",
        "https://two.example",
    ]
    assert settings.DEFAULT_GUARDRAIL_TRIGGERS == ["first trigger", "second trigger"]
