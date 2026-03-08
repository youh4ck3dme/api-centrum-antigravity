import pytest
from app.dns_monitor.monitor import detect_threats

def test_detect_threats_ttl_change():
    domain = "test.com"
    prev = [
        {"type": "A", "name": "test.com", "content": "1.1.1.1", "ttl": 3600}
    ]
    curr = [
        {"type": "A", "name": "test.com", "content": "1.1.1.1", "ttl": 60}
    ]
    
    threats = detect_threats(domain, prev, curr)
    assert len(threats) == 1
    assert threats[0]["severity"] == "HIGH"
    assert "TTL zmenené" in threats[0]["message"]
    assert threats[0]["old_value"] == "3600"
    assert threats[0]["new_value"] == "60"

def test_detect_threats_spf_include_added():
    domain = "test.com"
    prev = [
        {"type": "TXT", "name": "test.com", "content": "v=spf1 include:_spf.google.com ~all", "ttl": 3600}
    ]
    curr = [
        {"type": "TXT", "name": "test.com", "content": "v=spf1 include:_spf.google.com include:attacker.com ~all", "ttl": 3600}
    ]
    
    threats = detect_threats(domain, prev, curr)
    assert len(threats) == 1
    assert threats[0]["severity"] == "HIGH"
    assert "SPF pridané include (attacker.com)" in threats[0]["message"]

def test_detect_threats_txt_disappeared():
    domain = "test.com"
    prev = [
        {"type": "TXT", "name": "test.com", "content": "some-verification-token", "ttl": 3600}
    ]
    curr = []
    
    threats = detect_threats(domain, prev, curr)
    assert len(threats) == 1
    assert threats[0]["severity"] == "HIGH"
    assert "TXT záznamy zmizli" in threats[0]["message"]

def test_detect_threats_a_record_changed():
    domain = "test.com"
    prev = [
        {"type": "A", "name": "test.com", "content": "1.1.1.1", "ttl": 3600}
    ]
    curr = [
        {"type": "A", "name": "test.com", "content": "2.2.2.2", "ttl": 3600}
    ]
    
    threats = detect_threats(domain, prev, curr)
    assert len(threats) == 1
    assert threats[0]["severity"] == "CRITICAL"
    assert "A record zmenený" in threats[0]["message"]

def test_detect_threats_no_baseline():
    domain = "test.com"
    prev = []
    curr = [{"type": "A", "name": "test.com", "content": "1.1.1.1", "ttl": 3600}]
    
    threats = detect_threats(domain, prev, curr)
    assert len(threats) == 0
