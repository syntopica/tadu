// The JSON body of a board response; a refused or failed request throws an
// Error carrying the HTTP status (0 when the server could not be reached)
// and the server's message.
export async function responseBody(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.error ?? `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}
