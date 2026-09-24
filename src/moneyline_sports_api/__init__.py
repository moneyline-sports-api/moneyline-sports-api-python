"""Official Python SDK for MoneyLine Sports API: live odds, player props, hit rates, +EV, arbitrage and scores."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

__version__ = "0.1.1"
__all__ = ["MoneyLine", "MoneyLineError", "DEFAULT_BASE_URL"]

DEFAULT_BASE_URL = "https://mlapi.bet"
DEFAULT_TIMEOUT_S = 15.0


class MoneyLineError(Exception):
    """A failed API call, with the HTTP status, the stable error code, and the request id for support."""

    def __init__(self, message: str, status: int, code: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id


class MoneyLine:
    """MoneyLine Sports API client. The API key defaults to the MONEYLINE_API_KEY environment variable."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT_S):
        self.api_key = api_key or os.environ.get("MONEYLINE_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, query: Optional[dict] = None, body: Any = None) -> dict:
        """Call any endpoint and return the full response envelope (data + meta)."""
        params = {k: v for k, v in (query or {}).items() if v is not None}
        url = self.base_url + path + ("?" + urllib.parse.urlencode(params) if params else "")
        headers = {"accept": "application/json", "user-agent": f"moneyline-sports-api-python/{__version__}"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        data = None
        if body is not None:
            headers["content-type"] = "application/json"
            data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                status, raw = res.status, res.read()
        except urllib.error.HTTPError as err:
            status, raw = err.code, err.read()
        try:
            payload = json.loads(raw or b"null")
        except ValueError:
            payload = None
        if status >= 400 or not isinstance(payload, dict) or not payload.get("success"):
            envelope = payload if isinstance(payload, dict) else {}
            error, meta = envelope.get("error") or {}, envelope.get("meta") or {}
            raise MoneyLineError(error.get("message") or f"HTTP {status}", status, error.get("code"), meta.get("requestId"))
        return payload

    def get(self, path: str, **query: Any) -> Any:
        """GET an endpoint and return only its data."""
        return self.request("GET", path, query)["data"]

    def coverage(self) -> Any:
        """Live counts of leagues, books and markets. No API key needed."""
        return self.get("/public/coverage")

    def sports(self) -> Any:
        return self.get("/v1/sports")

    def leagues(self, sport: Optional[str] = None) -> Any:
        return self.get("/v1/leagues", sport=sport)

    def events(self, **query: Any) -> Any:
        return self.get("/v1/events", **query)

    def event(self, event_id: str) -> Any:
        return self.get(f"/v1/events/{urllib.parse.quote(event_id, safe='')}")

    def live_events(self, league: Optional[str] = None) -> Any:
        return self.get("/v1/events/live", league=league)

    def odds(self, **query: Any) -> Any:
        return self.get("/v1/odds", **query)

    def event_odds(self, event_id: str, **query: Any) -> Any:
        return self.get(f"/v1/events/{urllib.parse.quote(event_id, safe='')}/odds", **query)

    def bookmakers(self, source_type: Optional[str] = None) -> Any:
        return self.get("/v1/odds/bookmakers", sourceType=source_type)

    def player_props(self, **query: Any) -> Any:
        return self.get("/v1/player-props", **query)

    def hit_rates(self, player_id: str, *, market: str, line: float, **query: Any) -> Any:
        """Hit rates for one prop. The API rejects a call without both `market` and `line`."""
        path = f"/v1/players/{urllib.parse.quote(player_id, safe='')}/hit-rates"
        return self.get(path, market=market, line=line, **query)

    def ev_bets(self, **query: Any) -> Any:
        return self.get("/v1/edge/ev", **query)

    def value_bets(self, **query: Any) -> Any:
        return self.get("/v1/edge/value", **query)

    def arbitrage(self, **query: Any) -> Any:
        return self.get("/v1/edge/arbitrage", **query)

    def best_bets(self, **query: Any) -> Any:
        return self.get("/v1/best-bets", **query)

    def ask(self, message: str, **options: Any) -> Any:
        """MoneyLine AI: a data-grounded answer to a betting question."""
        body = {"messages": [{"role": "user", "content": message}], **options}
        return self.request("POST", "/v1/ai/chat", body=body)["data"]
