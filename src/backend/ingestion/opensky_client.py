from typing import Any

import httpx

from app.core.config import get_settings


class OpenSkyClient:
    """Thin wrapper over OpenSky /states/all."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        settings = get_settings()
        self._base_url = settings.opensky_base_url.rstrip("/")
        auth: tuple[str, str] | None = None
        if settings.opensky_username and settings.opensky_password:
            auth = (settings.opensky_username, settings.opensky_password)
        self._client = client or httpx.Client(timeout=30.0, auth=auth)

    def fetch_states(self) -> dict[str, Any]:
        resp = self._client.get(f"{self._base_url}/states/all")
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._client.close()
