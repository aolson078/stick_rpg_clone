"""Tests for configurable key bindings."""

import json

import settings


def test_key_bindings_override(tmp_path, monkeypatch):
    cfg = tmp_path / "keybindings.json"
    cfg.write_text(json.dumps({"move_up": [42]}))
    orig_file = settings.KEY_BINDINGS_FILE
    orig_bindings = dict(settings.KEY_BINDINGS)
    monkeypatch.setattr(settings, "KEY_BINDINGS_FILE", str(cfg))
    with open(cfg) as f:
        loaded = json.load(f)
    settings.KEY_BINDINGS.update({k: [int(v) for v in vals] for k, vals in loaded.items()})
    assert settings.KEY_BINDINGS["move_up"] == [42]
    settings.KEY_BINDINGS = orig_bindings
    settings.KEY_BINDINGS_FILE = orig_file

