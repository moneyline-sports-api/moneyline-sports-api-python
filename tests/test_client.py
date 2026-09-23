import io
import json
import unittest
import urllib.error
from unittest import mock

from moneyline_sports_api import MoneyLine, MoneyLineError


class FakeResponse(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ClientTest(unittest.TestCase):
    def test_sends_key_drops_none_and_returns_data(self):
        seen = {}

        def fake(req, timeout):
            seen["url"], seen["key"] = req.full_url, req.get_header("X-api-key")
            return FakeResponse(json.dumps({"success": True, "data": [1], "meta": {}, "error": None}).encode())

        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(MoneyLine(api_key="k").odds(league="nfl", market=None), [1])
        self.assertEqual(seen["url"], "https://mlapi.bet/v1/odds?league=nfl")
        self.assertEqual(seen["key"], "k")

    def test_raises_with_api_error_code(self):
        body = json.dumps({"success": False, "data": None, "meta": {"requestId": "r1"},
                           "error": {"message": "Invalid key", "statusCode": 401, "code": "ERR_API_KEY_INVALID"}}).encode()

        def fake(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(body))

        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(MoneyLineError) as ctx:
                MoneyLine(api_key="bad").sports()
        self.assertEqual((ctx.exception.status, ctx.exception.code, ctx.exception.request_id), (401, "ERR_API_KEY_INVALID", "r1"))


if __name__ == "__main__":
    unittest.main()
