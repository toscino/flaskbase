"""Smoke tests for the flask-base package."""

from flask_base import FlaskApp


def test_import_flask_app():
    assert FlaskApp is not None


def test_flask_app_version():
    from flask_base.flask_base import __version__

    assert __version__ == "0.3.0"


def test_flask_app_creates_app():
    manager = FlaskApp("Test App", demo_user="demo")
    assert manager.app is not None
    assert manager.app_name == "Test App"
