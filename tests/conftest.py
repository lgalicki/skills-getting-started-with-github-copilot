import pytest
from httpx import AsyncClient, ASGITransport
import importlib.util
import sys
from pathlib import Path


def get_app():
    # Try common import locations for the FastAPI app.
    try:
        from app.main import app as _app
        return _app
    except Exception:
        pass
    try:
        from main import app as _app
        return _app
    except Exception:
        pass
    try:
        from src.main import app as _app
        return _app
    except Exception:
        pass

    # Fallback: import the src/app.py by path inside this repository
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "src" / "app.py"
    if candidate.exists():
        spec = importlib.util.spec_from_file_location("repo.app_module", str(candidate))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "app"):
            return getattr(module, "app")

    raise RuntimeError(
        "Could not import FastAPI 'app'. Update get_app() in tests/conftest.py with the correct import path."
    )


@pytest.fixture
async def async_client():
    app = get_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
