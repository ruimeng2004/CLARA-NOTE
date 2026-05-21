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


def test_deepseek_provider_uses_deepseek_base_url(monkeypatch):
    monkeypatch.setenv("CLARA_LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("CLARA_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("CLARA_LLM_MODEL", raising=False)

    from clara_agent.llm import DEEPSEEK_BASE_URL, get_base_url, get_model, get_provider

    assert get_provider() == "deepseek"
    assert get_base_url() == DEEPSEEK_BASE_URL
    assert get_model() == "deepseek-v4-flash"
