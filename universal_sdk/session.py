"""Session class for API."""

from typing import Optional, Dict, Any, Tuple
import httpx
import json
import gzip

from .shared import build_headers, validate_response
from .akamai_input import SensorInput, PixelInput, SbsdInput

#: Default API base url used when none is configured.
DEFAULT_BASE_URL = "https://sold-out.dev"

class Session:
    def __init__(self, api_key: str, jwt_key: Optional[str] = None, app_key: Optional[str] = None,
                 app_secret: Optional[str] = None, client: Optional[httpx.Client] = None,
                 compression: bool = True, base_url: Optional[str] = None) -> None:
        """
        Creates a new session.

        ``jwt_key``, ``app_key`` and ``app_secret`` are accepted and ignored: they exist
        only so code written against the upstream SDK keeps working unchanged. This API
        authenticates with the API key alone.
        """
        self.api_key = api_key
        self.client = httpx.Client(timeout=httpx.Timeout(30.0)) if client is None else client
        self._owns_client = client is None
        self.compression = compression
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_client and self.client:
            self.client.close()

    def close(self):
        """Close the client if we own it."""
        if self._owns_client and self.client:
            self.client.close()

    def generate_sensor_data(self, input_data: SensorInput) -> Tuple[str, str]:
        """
        Returns the sensor data required to generate valid akamai cookies using the API.

        Args:
            input_data (SensorInput): An instance of SensorInput containing the necessary data for generating the sensor data.

        Returns:
            str: Sensor data as a string.
            str: Context data as a string.
        """
        sensor_endpoint = f"{self.base_url}/v3/sensor"

        headers = self._build_headers()
        payload_data = {
            'userAgent': input_data.user_agent,
            'abck': input_data.abck,
            'bmsz': input_data.bmsz,
            'version': input_data.version,
            'pageUrl': input_data.page_url,
            'script': input_data.script,
            'scriptUrl': input_data.script_url,
            'context': input_data.context,
            'ip': input_data.ip,
            'acceptLanguage': input_data.accept_language,
        }
        payload = json.dumps(payload_data).encode('utf-8')

        # Compress payload if large enough
        payload, use_compression = self._compress_payload(payload)
        if use_compression:
            headers["content-encoding"] = "gzip"

        response = self.client.post(sensor_endpoint, headers=headers, content=payload)

        # Decompress response if needed
        response_content = self._decompress_response(response)
        response_data = json.loads(response_content)
        validate_response(response_data, response.status_code)

        return response_data["payload"], response_data.get("context", "")

    def generate_sbsd_data(self, input_data: SbsdInput) -> str:
        """
        Returns the sbsd data required to solve SBSD using the API.

        Args:
            input_data (SbsdInput): An instance of SbsdInput containing the necessary data for generating the sbsd data.

        Returns:
            str: Sensor data as a string.
        """
        sensor_endpoint = f"{self.base_url}/sbsd"
        return self._send_request(sensor_endpoint, {
            'userAgent': input_data.user_agent,
            'uuid': input_data.uuid,
            'pageUrl': input_data.page_url,
            'o': input_data.o_cookie,
            'script': input_data.script,
            'acceptLanguage': input_data.accept_language,
            'ip': input_data.ip,
            'index': input_data.index,
        })

    def generate_pixel_data(self, input_data: PixelInput) -> str:
        """
        Returns the pixel data using the API.

        Args:
            input_data (PixelInput): An instance of PixelInput containing the necessary data for generating the pixel data.

        Returns:
            str: Pixel data as a string.
        """
        pixel_endpoint = f"{self.base_url}/pixel"
        return self._send_request(pixel_endpoint, {
            'userAgent': input_data.user_agent,
            'htmlVar': input_data.html_var,
            'scriptVar': input_data.script_var,
            'ip': input_data.ip,
            'acceptLanguage': input_data.accept_language,
        })

    def _build_headers(self) -> Dict[str, str]:
        """
        Builds the headers dictionary for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with all required authentication headers
        """
        headers = build_headers(self.api_key)
        # Add compression headers
        if self.compression:
            headers["accept-encoding"] = "gzip"
        return headers

    def _compress_payload(self, payload: bytes) -> Tuple[bytes, bool]:
        """
        Compresses the payload using gzip if enabled and payload is large enough.

        Args:
            payload (bytes): The payload to potentially compress

        Returns:
            Tuple[bytes, bool]: The (potentially compressed) payload and whether compression was used
        """
        if not self.compression or len(payload) <= 1000:
            return payload, False

        try:
            compressed = gzip.compress(payload, compresslevel=6)
            return compressed, True
        except Exception:
            # Fall back to uncompressed if compression fails
            return payload, False

    def _decompress_response(self, response: httpx.Response) -> bytes:
        """
        Decompresses the response body if it's compressed with gzip.

        Args:
            response (httpx.Response): The HTTP response

        Returns:
            bytes: The decompressed response body
        """
        content = response.content
        content_encoding = response.headers.get("content-encoding", "").lower()

        if content_encoding == "gzip" and self.compression:
            try:
                return gzip.decompress(content)
            except Exception:
                # Fall back to original content if decompression fails
                pass

        return content

    def _send_request(self, url: str, input_data: Dict[str, Any]) -> str:
        """
        Sends a request and returns the payload.

        Args:
            url (str): The endpoint URL
            input_data (Dict[str, Any]): The request data

        Returns:
            str: The response payload
        """
        headers = self._build_headers()
        payload = json.dumps(input_data).encode('utf-8')

        # Compress payload if large enough
        payload, use_compression = self._compress_payload(payload)
        if use_compression:
            headers["content-encoding"] = "gzip"

        response = self.client.post(url, headers=headers, content=payload)

        # Decompress response if needed
        response_content = self._decompress_response(response)
        response_data = json.loads(response_content)
        validate_response(response_data, response.status_code)
        return response_data["payload"]
