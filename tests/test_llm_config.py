from clara_agent.llm import GPTSAPI_BASE_URL, get_base_url, get_provider


def test_gptsapi_provider_uses_gptsapi_base_url(monkeypatch):
    monkeypatch.setenv("CLARA_LLM_PROVIDER", "gptsapi")
    monkeypatch.delenv("CLARA_LLM_BASE_URL", raising=False)

    assert get_provider() == "gptsapi"
    assert get_base_url() == GPTSAPI_BASE_URL


def test_custom_base_url_overrides_provider_default(monkeypatch):
    monkeypatch.setenv("CLARA_LLM_PROVIDER", "gptsapi")
    monkeypatch.setenv("CLARA_LLM_BASE_URL", "https://example.com/v1/")

    assert get_base_url() == "https://example.com/v1"
