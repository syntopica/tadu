import json

from tadu.json_error import json_error


def test_status_body_and_type() -> None:
    status, body, content_type = json_error(404, "not found")
    assert (status, content_type) == (404, "application/json; charset=utf-8")
    assert json.loads(body) == {"error": "not found"}
