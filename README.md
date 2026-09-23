# MoneyLine Sports API for Python

The official Python SDK for [MoneyLine Sports API](https://www.moneylineapp.com). Use it to get live odds, player props, hit rates, +EV and arbitrage signals, and scores for NFL, NBA, MLB, NHL, college football, college basketball, EPL, MLS and the World Cup, all through one API.

See what's covered right now, including leagues, sportsbooks, DFS apps and exchanges, at [moneylineapp.com/coverage](https://www.moneylineapp.com/coverage).

## Install

```bash
pip install moneyline-sports-api
```

The SDK needs Python 3.9 or later and has no dependencies.

## Get an API key

[Sign up for a free key](https://www.moneylineapp.com/signup). The SDK reads it from the `MONEYLINE_API_KEY` environment variable, or you can pass it in yourself:

```python
from moneyline_sports_api import MoneyLine

ml = MoneyLine(api_key="your-key")
```

## Examples

```python
# Today's NFL odds across every book
odds = ml.odds(league="nfl")

# Player props for one player
props = ml.player_props(league="nba", player="Jayson Tatum")

# Positive expected-value bets and arbitrage
ev = ml.ev_bets(league="nfl", limit=10)
arbs = ml.arbitrage(league="mlb")

# Hit rates over the last 5, 10 and 25 games and the season
# (player IDs come back on every player-prop record)
rates = ml.hit_rates(player_id, market="player_points")

# Ask MoneyLine AI a question grounded in live data
answer = ml.ask("Best NBA player props tonight?")

# Live coverage counts (no key needed)
coverage = ml.coverage()
```

Every other endpoint is reachable through `ml.get(path, **query)`, which returns the response data. To get `data` and `meta` together, use `ml.request("GET", path, query)`.

## Errors

A failed call raises `MoneyLineError` with the HTTP `status`, a stable `code` such as `ERR_API_KEY_INVALID` or `ERR_CREDIT_LIMIT`, and a `request_id` to include when you contact support.

```python
from moneyline_sports_api import MoneyLineError

try:
    ml.odds(league="nfl")
except MoneyLineError as err:
    if err.status == 429:
        pass  # You hit the rate limit. Wait, then try again.
```

Each request times out after 15 seconds. To change that, pass `timeout`.

## Links

- [Documentation](https://www.moneylineapp.com/docs)
- [Live coverage](https://www.moneylineapp.com/coverage)
- [OpenAPI spec](https://mlapi.bet/openapi.json)
- [Pricing](https://www.moneylineapp.com/pricing)
- [JavaScript SDK](https://github.com/moneyline-sports-api/moneyline-sports-api-js)

MIT licensed.
