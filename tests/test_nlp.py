import pytest
from app.services.nlp_service import nlp_service

@pytest.fixture(scope="module", autouse=True)
def load_nlp():
    nlp_service.load()

def test_spell_check_simple():
    text = "Thiss is a test."
    corrections = nlp_service.check_text(text)
    assert len(corrections) > 0
    assert corrections[0]["word"] == "Thiss"
    assert corrections[0]["correction"] == "This"

def test_medical_whitelist():
    # 'Hyperlipidemia' is in medical_terms.txt
    text = "Check for hyperlipidemia"
    corrections = nlp_service.check_text(text)
    # It should NOT find corrections for whitelisted words
    for c in corrections:
        assert c["word"].lower() != "hyperlipidemia"
