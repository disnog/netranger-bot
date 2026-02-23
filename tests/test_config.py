# tests/test_config.py
# Unit tests for network_ranger/config.py.

from __future__ import annotations

import pytest

from network_ranger.config import Config


# ---------------------------------------------------------------------------
# Config.from_env() — required fields
# ---------------------------------------------------------------------------

def test_from_env_loads_required_fields(minimal_env):
    config = Config.from_env()

    assert config.token == "test-token-abc"
    assert config.guild_id == 987654321


def test_from_env_raises_on_missing_token(monkeypatch):
    monkeypatch.setenv("GUILD_ID", "123")
    monkeypatch.delenv("TOKEN", raising=False)

    with pytest.raises(ValueError, match="TOKEN"):
        Config.from_env()


def test_from_env_raises_on_missing_guild_id(monkeypatch):
    monkeypatch.setenv("TOKEN", "tok")
    monkeypatch.delenv("GUILD_ID", raising=False)

    with pytest.raises(ValueError, match="GUILD_ID"):
        Config.from_env()


def test_from_env_guild_id_is_int(minimal_env):
    config = Config.from_env()
    assert isinstance(config.guild_id, int)


# ---------------------------------------------------------------------------
# Config.from_env() — optional fields with defaults
# ---------------------------------------------------------------------------

def test_from_env_channel_defaults(minimal_env):
    config = Config.from_env()

    assert config.welcome_channel == "welcome"
    assert config.member_channel == "general"
    assert config.log_channel == "cnc"
    assert config.mirror_channel == "mirror"


def test_from_env_role_default(minimal_env):
    config = Config.from_env()
    assert config.member_role == "Members"


def test_from_env_email_defaults_to_none(minimal_env):
    config = Config.from_env()

    assert config.smtp_server is None
    assert config.smtp_username is None
    assert config.smtp_password is None
    assert config.smtp_from is None
    assert config.secret_key is None


def test_from_env_smtp_port_default(minimal_env):
    config = Config.from_env()
    assert config.smtp_port == 587


# ---------------------------------------------------------------------------
# Config.from_env() — custom optional values
# ---------------------------------------------------------------------------

def test_from_env_custom_channels(full_env):
    config = Config.from_env()

    assert config.welcome_channel == "arrivals"
    assert config.member_channel == "lounge"
    assert config.log_channel == "audit-log"
    assert config.mirror_channel == "mirror-log"


def test_from_env_custom_smtp(full_env):
    config = Config.from_env()

    assert config.smtp_server == "mail.example.com"
    assert config.smtp_port == 465
    assert config.smtp_username == "bot@example.com"
    assert config.smtp_password == "s3cr3t"
    assert config.smtp_from == "noreply@example.com"


def test_from_env_custom_description(full_env):
    config = Config.from_env()
    assert config.description == "Test Ranger"


def test_from_env_smtp_port_is_int(full_env):
    config = Config.from_env()
    assert isinstance(config.smtp_port, int)


# ---------------------------------------------------------------------------
# Config.email_configured property
# ---------------------------------------------------------------------------

def test_email_configured_true(full_env):
    config = Config.from_env()
    assert config.email_configured is True


def test_email_configured_false_missing_server(full_env, monkeypatch):
    monkeypatch.delenv("SMTP_SERVER")
    config = Config.from_env()
    assert config.email_configured is False


def test_email_configured_false_missing_username(full_env, monkeypatch):
    monkeypatch.delenv("SMTP_USERNAME")
    config = Config.from_env()
    assert config.email_configured is False


def test_email_configured_false_missing_password(full_env, monkeypatch):
    monkeypatch.delenv("SMTP_PASSWORD")
    config = Config.from_env()
    assert config.email_configured is False


def test_email_configured_false_missing_from(full_env, monkeypatch):
    monkeypatch.delenv("SMTP_FROMEMAIL")
    config = Config.from_env()
    assert config.email_configured is False


def test_email_configured_false_missing_secret_key(full_env, monkeypatch):
    monkeypatch.delenv("SECRETKEY")
    config = Config.from_env()
    assert config.email_configured is False


def test_email_configured_false_when_all_missing(minimal_env):
    config = Config.from_env()
    assert config.email_configured is False


# ---------------------------------------------------------------------------
# Config dataclass direct construction
# ---------------------------------------------------------------------------

def test_direct_construction():
    config = Config(token="tok", guild_id=999)
    assert config.token == "tok"
    assert config.guild_id == 999
    assert config.command_prefix == "/"
    assert config.email_configured is False
