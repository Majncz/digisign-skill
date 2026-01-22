#!/usr/bin/env python3
"""Shared utilities for DigiSign API operations."""

import json
import os
import sys
import time
from pathlib import Path
from typing import Iterator, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# Exceptions
class DigiSignError(Exception):
    """Base exception for DigiSign API errors."""
    pass


class AuthenticationError(DigiSignError):
    """Authentication failed."""
    pass


class RateLimitError(DigiSignError):
    """Rate limit exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(DigiSignError):
    """API validation error with field details."""
    def __init__(self, message: str, violations: list):
        super().__init__(message)
        self.violations = violations


class NotFoundError(DigiSignError):
    """Resource not found."""
    pass


class ForbiddenError(DigiSignError):
    """Operation not permitted."""
    pass


# Configuration
DEFAULT_TOKEN_FILE = Path.home() / ".digisign" / "token.json"
DEFAULT_BASE_URL = "https://api.digisign.org"


def get_config() -> dict:
    """Load configuration from environment variables.

    Required (one of):
        DIGISIGN_ACCESS_KEY + DIGISIGN_SECRET_KEY: For token exchange
        DIGISIGN_ACCESS_TOKEN: Direct JWT token

    Optional:
        DIGISIGN_API_URL: API base URL (default: https://api.digisign.org)
        DIGISIGN_TOKEN_FILE: Path to token file (default: ~/.digisign/token.json)
    """
    config = {
        "access_key": os.environ.get("DIGISIGN_ACCESS_KEY"),
        "secret_key": os.environ.get("DIGISIGN_SECRET_KEY"),
        "access_token": os.environ.get("DIGISIGN_ACCESS_TOKEN"),
        "base_url": os.environ.get("DIGISIGN_API_URL", DEFAULT_BASE_URL).rstrip("/"),
        "token_file": Path(os.environ.get("DIGISIGN_TOKEN_FILE", DEFAULT_TOKEN_FILE)),
    }
    return config


def get_headers(access_token: str, content_type: Optional[str] = None, accept_language: Optional[str] = None) -> dict:
    """Build request headers with Authorization."""
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    if accept_language:
        headers["Accept-Language"] = accept_language
    return headers


def handle_response(response, expected_status: list[int] = None) -> dict:
    """Handle API response, raise on errors."""
    if expected_status is None:
        expected_status = [200, 201]

    status = response.status if hasattr(response, 'status') else response.code

    if status == 204:
        return {}

    try:
        data = json.loads(response.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = {}

    if status in expected_status:
        return data

    if status == 400:
        violations = data.get("violations", [])
        message = data.get("detail", "Bad request")
        raise ValidationError(message, violations)

    if status == 401:
        raise AuthenticationError(data.get("detail", "Authentication failed"))

    if status == 403:
        raise ForbiddenError(data.get("detail", "Operation forbidden"))

    if status == 404:
        raise NotFoundError(data.get("detail", "Resource not found"))

    if status == 422:
        violations = data.get("violations", [])
        message = data.get("detail", "Validation failed")
        raise ValidationError(message, violations)

    if status == 429:
        retry_after = response.headers.get("Retry-After") if hasattr(response, 'headers') else None
        raise RateLimitError(
            "Rate limit exceeded",
            int(retry_after) if retry_after else None
        )

    raise DigiSignError(f"API error {status}: {data}")


def api_request(
    method: str,
    endpoint: str,
    access_token: str,
    data: dict = None,
    params: dict = None,
    expected_status: list[int] = None,
    base_url: str = None,
    accept_language: str = None
) -> dict:
    """Make authenticated API request.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        endpoint: API endpoint (e.g., /api/envelopes)
        access_token: JWT access token
        data: Request body (for POST/PATCH)
        params: Query parameters
        expected_status: List of acceptable status codes
        base_url: Override base URL
        accept_language: Accept-Language header for localized responses

    Returns:
        Parsed JSON response
    """
    if base_url is None:
        base_url = get_config()["base_url"]

    url = f"{base_url}{endpoint}"

    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if query:
            url = f"{url}?{query}"

    headers = get_headers(
        access_token,
        content_type="application/json" if data else None,
        accept_language=accept_language
    )

    body = json.dumps(data).encode("utf-8") if data else None

    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            return handle_response(response, expected_status)
    except HTTPError as e:
        return handle_response(e, expected_status)


def api_request_binary(
    method: str,
    endpoint: str,
    access_token: str,
    expected_status: list[int] = None,
    base_url: str = None
) -> bytes:
    """Make authenticated API request expecting binary response.

    Args:
        method: HTTP method
        endpoint: API endpoint
        access_token: JWT access token
        expected_status: List of acceptable status codes
        base_url: Override base URL

    Returns:
        Raw bytes response
    """
    if base_url is None:
        base_url = get_config()["base_url"]
    if expected_status is None:
        expected_status = [200]

    url = f"{base_url}{endpoint}"
    headers = get_headers(access_token)

    req = Request(url, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            if response.status not in expected_status:
                raise DigiSignError(f"Unexpected status {response.status}")
            return response.read()
    except HTTPError as e:
        handle_response(e, expected_status)


def upload_file(
    file_path: str,
    access_token: str,
    base_url: str = None
) -> dict:
    """Upload a file using multipart/form-data.

    Args:
        file_path: Path to file to upload
        access_token: JWT access token
        base_url: Override base URL

    Returns:
        Parsed JSON response with file ID
    """
    import mimetypes
    from uuid import uuid4

    if base_url is None:
        base_url = get_config()["base_url"]

    url = f"{base_url}/api/files"
    boundary = f"----WebKitFormBoundary{uuid4().hex[:16]}"

    file_path = Path(file_path)
    filename = file_path.name
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = Request(url, data=body, headers=headers, method="POST")

    try:
        with urlopen(req) as response:
            return handle_response(response, [200, 201])
    except HTTPError as e:
        return handle_response(e, [200, 201])


def paginate(
    endpoint: str,
    access_token: str,
    params: dict = None,
    max_pages: int = None,
    base_url: str = None
) -> Iterator[dict]:
    """Iterate through paginated results.

    Args:
        endpoint: API endpoint
        access_token: JWT access token
        params: Query parameters
        max_pages: Maximum pages to fetch (None for all)
        base_url: Override base URL

    Yields:
        Individual records from paginated response
    """
    if params is None:
        params = {}

    page = 1
    while True:
        params["page"] = page
        results = api_request("GET", endpoint, access_token, params=params, base_url=base_url)

        # DigiSign returns items in different formats
        if isinstance(results, list):
            items = results
        elif isinstance(results, dict):
            # Try different response formats: items, hydra:member, member
            items = results.get("items", results.get("hydra:member", results.get("member", [])))
        else:
            items = []

        if not items:
            break

        for item in items:
            yield item

        # Check if there are more pages
        if isinstance(results, dict):
            # Check for next page in links or by count
            total = results.get("count", 0)
            items_per_page = results.get("itemsPerPage", 30)
            if page * items_per_page >= total:
                break
            # Also check hydra format
            view = results.get("hydra:view", {})
            if view and not view.get("hydra:next"):
                break
        elif len(items) < 30:  # Default page size
            break

        page += 1
        if max_pages and page > max_pages:
            break


def load_token(token_file: Path = None) -> dict:
    """Load token from file.

    Returns dict with token, exp, iat
    """
    if token_file is None:
        token_file = get_config()["token_file"]

    if not token_file.exists():
        raise AuthenticationError(f"Token file not found: {token_file}")

    with open(token_file) as f:
        return json.load(f)


def save_token(token_data: dict, token_file: Path = None) -> None:
    """Save token to file with secure permissions."""
    if token_file is None:
        token_file = get_config()["token_file"]

    token_file.parent.mkdir(parents=True, exist_ok=True)

    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)

    # Set file permissions to owner read/write only
    os.chmod(token_file, 0o600)


def get_access_token() -> str:
    """Get access token from environment or token file.

    Checks in order:
    1. DIGISIGN_ACCESS_TOKEN env var
    2. Token file

    Returns access token string.
    """
    config = get_config()

    # Direct token from env
    if config["access_token"]:
        return config["access_token"]

    # Token file
    try:
        token_data = load_token(config["token_file"])

        # Check if expired
        exp = token_data.get("exp", 0)
        if time.time() >= exp - 60:  # 1 minute buffer
            raise AuthenticationError("Token expired. Run 'python auth.py get-token --save' to get a new one.")

        return token_data["token"]
    except (FileNotFoundError, KeyError):
        pass

    raise AuthenticationError(
        "No access token available. Run 'python auth.py get-token --save' first."
    )


def format_output(data, output_format: str = "json") -> str:
    """Format output data."""
    if output_format == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format == "id":
        if isinstance(data, list):
            return "\n".join(str(item.get("id", "")) for item in data)
        return str(data.get("id", ""))
    else:
        return str(data)


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_json(data) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def confirm(message: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"{message} [y/N]: ").strip().lower()
    return response in ("y", "yes")
