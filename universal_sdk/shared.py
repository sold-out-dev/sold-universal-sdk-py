"""Shared utility functions for both sync and async Session classes."""

from typing import Dict


def build_headers(api_key: str) -> Dict[str, str]:
    """
    Builds the headers dictionary used for every API request.

    Args:
        api_key (str): The API key for authentication

    Returns:
        Dict[str, str]: Headers dictionary with all required authentication headers

    Raises:
        ValueError: If api_key is not provided
    """
    if not api_key:
        raise ValueError("Missing API key")

    return {
        'Content-Type': 'application/json',
        'X-Api-Key': api_key,
    }


def validate_response(response_data: dict, status_code: int) -> None:
    """
    Validates the API response and raises exceptions if there are errors.

    Args:
        response_data (dict): The parsed JSON response
        status_code (int): The HTTP status code

    Raises:
        Exception: If there's an error in the response or status code is not 200
    """
    if "error" in response_data and response_data["error"]:
        raise Exception(f"API returned with error: {response_data['error']}")

    if status_code != 200:
        raise Exception(f"API returned with status code: {status_code}")
