from tadu.default_http_port import DEFAULT_HTTP_PORT


def test_default_http_port_is_80() -> None:
    assert DEFAULT_HTTP_PORT == 80
