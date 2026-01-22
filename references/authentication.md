# Authentication

DigiSign uses Bearer token authentication (RFC 6750). You must exchange your API credentials for a JWT token before making API calls.

## API Key Setup

1. Log into DigiSign selfcare at https://app.digisign.org
2. Navigate to **Settings > For Developers > API Keys**
3. Click **"New API Key"**
4. Configure permissions:
   - **Read envelopes** - List and view envelopes
   - **Create envelopes** - Create new envelopes
   - **Send envelopes** - Send envelopes for signing
   - **Manage webhooks** - Create and manage webhooks
   - (and more granular permissions)
5. Optionally restrict to specific IP addresses
6. Save the `accessKey` and `secretKey` (shown only once!)

## Token Exchange

### Endpoint
```
POST /api/auth-token
```

### Request
```http
POST /api/auth-token HTTP/1.1
Host: api.digisign.org
Content-Type: application/json

{
  "accessKey": "wBzMakF4Cpl7hAt0QtzqRZ3d",
  "secretKey": "yV2ZqHyOmb8xqDe5kSxnyM6d3BEAMgT1v29gBpjEjrz8j7NyiVJ1yHqDHAiwrPFRzFDPsTkqlWVJwWxP"
}
```

### Response
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2ODI0ODU3MzIsImV4cCI6MTY4MjU3MjEzMiwicm9sZXMiOlsiUk9MRV9BUEkiXSwidXNlcm5hbWUiOiJhcGlfa2V5X2V0eTJiNTFidTJnN2JxbHV1bSJ9.Keeq-bJVYmQ",
  "exp": 1682572132,
  "iat": 1682485732
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `token` | string | JWT token for authentication |
| `exp` | integer | Token expiration (Unix timestamp) |
| `iat` | integer | Token issued at (Unix timestamp) |

Token validity is approximately **24 hours** (86400 seconds).

## Using the Token

Include the token in the `Authorization` header of all subsequent requests:

```http
GET /api/envelopes HTTP/1.1
Host: api.digisign.org
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

## Token Expiration

When the token expires, you'll receive a `401 Unauthorized` response:

```json
{
  "code": 401,
  "message": "Expired JWT Token"
}
```

Simply request a new token using your accessKey/secretKey.

## Code Examples

### JavaScript/TypeScript
```typescript
class DigiSignClient {
  private token: string | null = null;
  private tokenExp: number = 0;

  constructor(
    private accessKey: string,
    private secretKey: string,
    private baseUrl = 'https://api.digisign.org'
  ) {}

  async getToken(): Promise<string> {
    // Return cached token if still valid (with 5 min buffer)
    if (this.token && Date.now() / 1000 < this.tokenExp - 300) {
      return this.token;
    }

    const response = await fetch(`${this.baseUrl}/api/auth-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        accessKey: this.accessKey,
        secretKey: this.secretKey
      })
    });

    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.status}`);
    }

    const data = await response.json();
    this.token = data.token;
    this.tokenExp = data.exp;

    return this.token;
  }

  async request(method: string, path: string, body?: any): Promise<any> {
    const token = await this.getToken();

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: body ? JSON.stringify(body) : undefined
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.title || `Request failed: ${response.status}`);
    }

    return response.json();
  }
}

// Usage
const client = new DigiSignClient(
  process.env.DIGISIGN_ACCESS_KEY!,
  process.env.DIGISIGN_SECRET_KEY!
);

const envelopes = await client.request('GET', '/api/envelopes');
```

### Python
```python
import requests
import time
from typing import Optional, Any

class DigiSignClient:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        base_url: str = "https://api.digisign.org"
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self._token: Optional[str] = None
        self._token_exp: int = 0

    def get_token(self) -> str:
        # Return cached token if still valid (with 5 min buffer)
        if self._token and time.time() < self._token_exp - 300:
            return self._token

        response = requests.post(
            f"{self.base_url}/api/auth-token",
            json={
                "accessKey": self.access_key,
                "secretKey": self.secret_key
            }
        )
        response.raise_for_status()

        data = response.json()
        self._token = data["token"]
        self._token_exp = data["exp"]

        return self._token

    def request(
        self,
        method: str,
        path: str,
        json: Any = None,
        **kwargs
    ) -> Any:
        token = self.get_token()

        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=json,
            **kwargs
        )
        response.raise_for_status()

        return response.json() if response.content else None

# Usage
import os

client = DigiSignClient(
    os.environ["DIGISIGN_ACCESS_KEY"],
    os.environ["DIGISIGN_SECRET_KEY"]
)

envelopes = client.request("GET", "/api/envelopes")
```

### PHP
```php
<?php

class DigiSignClient
{
    private string $accessKey;
    private string $secretKey;
    private string $baseUrl;
    private ?string $token = null;
    private int $tokenExp = 0;

    public function __construct(
        string $accessKey,
        string $secretKey,
        string $baseUrl = 'https://api.digisign.org'
    ) {
        $this->accessKey = $accessKey;
        $this->secretKey = $secretKey;
        $this->baseUrl = $baseUrl;
    }

    public function getToken(): string
    {
        // Return cached token if still valid (with 5 min buffer)
        if ($this->token && time() < $this->tokenExp - 300) {
            return $this->token;
        }

        $ch = curl_init($this->baseUrl . '/api/auth-token');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_POSTFIELDS => json_encode([
                'accessKey' => $this->accessKey,
                'secretKey' => $this->secretKey,
            ]),
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("Authentication failed: $httpCode");
        }

        $data = json_decode($response, true);
        $this->token = $data['token'];
        $this->tokenExp = $data['exp'];

        return $this->token;
    }

    public function request(string $method, string $path, ?array $body = null): array
    {
        $token = $this->getToken();

        $ch = curl_init($this->baseUrl . $path);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $token,
                'Content-Type: application/json',
            ],
        ]);

        if ($body !== null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
        }

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode >= 400) {
            throw new Exception("Request failed: $httpCode - $response");
        }

        return json_decode($response, true) ?? [];
    }
}

// Usage
$client = new DigiSignClient(
    getenv('DIGISIGN_ACCESS_KEY'),
    getenv('DIGISIGN_SECRET_KEY')
);

$envelopes = $client->request('GET', '/api/envelopes');
```

## Error Responses

### Invalid Credentials
```json
{
  "code": 401,
  "message": "Invalid credentials."
}
```

### Missing Fields
```json
{
  "type": "https://tools.ietf.org/html/rfc2616#section-10",
  "title": "An error occurred",
  "status": 400,
  "violations": [
    {
      "propertyPath": "accessKey",
      "message": "This value should not be blank."
    }
  ]
}
```

### Disabled API Key
```json
{
  "code": 401,
  "message": "API key is disabled."
}
```

### IP Restriction
```json
{
  "code": 403,
  "message": "Access denied from this IP address."
}
```

## Security Best Practices

1. **Never expose credentials** in client-side code or version control
2. **Use environment variables** for credentials
3. **Restrict IP addresses** when possible in API key settings
4. **Use minimal permissions** - only enable what you need
5. **Rotate keys periodically** - create new key, update your app, delete old key
6. **Use staging environment** for testing to avoid accidental charges

## CLI Script Usage

```bash
# Set credentials
export DIGISIGN_ACCESS_KEY="your-access-key"
export DIGISIGN_SECRET_KEY="your-secret-key"

# Get token and save to ~/.digisign/token.json
python scripts/auth.py get-token --save

# Check token status
python scripts/auth.py status

# Clear saved token
python scripts/auth.py clear
```
