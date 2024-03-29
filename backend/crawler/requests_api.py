import logging
from typing import Any, Dict
from urllib.parse import urljoin

import requests
import tenacity
from cachecontrol import CacheControl
from fake_useragent import UserAgent
from ratelimit import limits, sleep_and_retry


logger = logging.getLogger(__name__) 


DEFAULT_TIMEOUT = 120  # Requests timeout in seconds
DEFAULT_RATE_LIMIT = 5  # Max 5 requests 2 seconds


class RequestsApi(requests.Session):
    """Client for making requests to an API."""

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT, **kwargs: Any) -> None:
        """Initialize session and base URL.

        Args:
            base_url (str): Base URL for API.
            kwargs: Additional keyword arguments passed to Session.
        """
        super().__init__()
        self.session = CacheControl(self)
        self.base_url = base_url
        self.user_agent = UserAgent()
        self.timeout = timeout

        # Set user agent on session
        self.headers["User-Agent"] = self.user_agent.random

        for arg in kwargs:
            if isinstance(kwargs[arg], dict):
                kwargs[arg] = self._deep_merge(getattr(self, arg), kwargs[arg])
            setattr(self, arg, kwargs[arg])

    def _build_url(self, endpoint):
        return urljoin(self.base_url, endpoint)

    def _deep_merge(
        self, source: Dict[str, Any], destination: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge source dict into destination dict recursively."""
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                self._deep_merge(value, node)
            else:
                destination[key] = value
        return destination

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    )
    @sleep_and_retry
    @limits(calls=DEFAULT_RATE_LIMIT, period=5)
    def make_request(
        self, method: str, url: str, timeout=None, **kwargs: Any
    ) -> requests.Response:
        """Construct and send a requests HTTP request."""
        url = self._build_url(url)
        if not timeout:
            timeout = self.timeout
        logger.info(f"Making {method} request to {url}")
        try:
            response = super().request(method, url, timeout=timeout, **kwargs)
            logger.info(f"Received {response.status_code} response from {url}")
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        return response

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Send a GET request.

        Args:
            url: URL for the request.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request("GET", url, headers=headers, **kwargs)

    def post(
        self, url: str, data: Any = None, json: Any = None, **kwargs: Any
    ) -> requests.Response:
        """Send a POST request.

        Args:
            url: URL for the request.
            data: Request body.
            json: JSON data to send.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request(
            "POST", url, headers=headers, data=data, json=json, **kwargs
        )

    def put(self, url: str, data: Any = None, **kwargs: Any) -> requests.Response:
        """Send a PUT request.

        Args:
            url: URL for the request.
            data: Request body.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request("PUT", url, headers=headers, data=data, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """Send a DELETE request.

        Args:
            url: URL for the request.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request("DELETE", url, headers=headers, **kwargs)

    def head(self, url: str, **kwargs: Any) -> requests.Response:
        """Send a HEAD request.

        Args:
            url: URL for the request.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request("HEAD", url, headers=headers, **kwargs)

    def patch(self, url: str, data: Any = None, **kwargs: Any) -> requests.Response:
        """Send a PATCH request.

        Args:
            url: URL for the request.
            data: Request body.
            kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response: The HTTP response.

        Raises:
            RequestException: If the request fails.
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent.random
        return self.make_request("PATCH", url, headers=headers, data=data, **kwargs)


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    client = RequestsApi("https://httpbin.org")
    response = client.get("/get")
    assert response.status_code == 200
    logger.info(response.json())
    
