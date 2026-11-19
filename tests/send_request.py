import http.client

from response import Response


def send_request(
    address: tuple[str, int], method: str, path: str, headers: dict[str, str]
) -> Response:
    """One request to the (host, port) address with exactly these headers, and what came back."""
    connection = http.client.HTTPConnection(*address, timeout=5)
    try:
        connection.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
        for name, value in headers.items():
            connection.putheader(name, value)
        connection.endheaders()
        reply = connection.getresponse()
        return Response(reply.status, reply.headers, reply.read())
    finally:
        connection.close()
