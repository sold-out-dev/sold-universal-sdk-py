# Universal SDK — Python

Python SDK for **Akamai Bot Manager**: sensor data generation, pixel and SBSD challenges, sec-cpt solving and `_abck` cookie validation. Sync and async clients included.

## 🔑 Getting API Access

Before using this SDK you need an API key:

1. Go to [sold-out.dev](https://sold-out.dev/), create an account and link your API key.
2. You can even ask for a **free trial** on our [Discord](https://discord.gg/NMRfsunxZ4).

## 📦 Installation

```bash
pip install sold-universal-sdk
```

## 🔧 Basic Usage

```python
from universal_sdk import Session, SensorInput

session = Session("your-api-key")

sensor_data, sensor_context = session.generate_sensor_data(SensorInput(
    # sensor input fields
))
```

Async version:

```python
from universal_sdk.session_async import SessionAsync

async with SessionAsync("your-api-key") as session:
    sensor_data, sensor_context = await session.generate_sensor_data(SensorInput(...))
```

### Session options

```python
session = Session(
    api_key="your-api-key",
    compression=True,
)
```

For drop-in compatibility with the upstream SDK, `jwt_key`, `app_key` and `app_secret` are
still accepted (positionally or by keyword) and ignored: this API authenticates with the
API key alone.

### Custom base URL

The API base url defaults to `DEFAULT_BASE_URL` (`https://sold-out.dev`). Override it with the `base_url` argument:

```python
from universal_sdk.session import DEFAULT_BASE_URL

session = Session("your-api-key", base_url="https://akamai.example.com")  # trailing slashes are stripped
print(session.base_url, DEFAULT_BASE_URL)
```

`SessionAsync` accepts the same argument.

## 🛡️ Akamai Bot Manager


### Handling Sec-Cpt Challenges

```python
from universal_sdk.akamai import SecCptChallenge

challenge = SecCptChallenge.parse(html_content)
# or: challenge = SecCptChallenge.parse_from_json(json_response)

payload = challenge.generate_sec_cpt_payload(sec_cpt_cookie)
challenge.sleep()
```

### Cookie Validation

```python
from universal_sdk.akamai import is_cookie_valid, is_cookie_invalidated

is_valid = is_cookie_valid(cookie_value, request_count)
needs_refresh = is_cookie_invalidated(cookie_value)
```


### Pixel Challenge Solving

```python
from universal_sdk import PixelInput
from universal_sdk.akamai import parse_pixel_html_var, parse_pixel_script_url, parse_pixel_script_var

html_var = parse_pixel_html_var(html_content)
script_url, post_url = parse_pixel_script_url(html_content)
script_var = parse_pixel_script_var(script_content)

pixel_data = session.generate_pixel_data(PixelInput(
    # pixel input fields
))
```

### SBSD Challenge Solving

```python
from universal_sdk import SbsdInput

sbsd_data = session.generate_sbsd_data(SbsdInput(
    # sbsd input fields
))
```

### Script Path Parsing

```python
from universal_sdk.akamai import parse_akamai_script_path

script_path = parse_akamai_script_path(html_content)
```

## 📄 License

MIT — see [LICENSE](LICENSE).

---

Fork of the Hyper Solutions SDK, trimmed down to the Akamai part and pointed at our own API.
