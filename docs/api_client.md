
example:

```python

from kuankr_utils.api_client import ApiClient

c = ApiClient('kuankr_stream')

#or set env: KUANKR_API_CLIENT=agutong.trader
#more: KUANKR_ADMIN_TOKEN, KUANKR_AUTH_TOKEN
headers = { 'x-api-client': 'agutong.trader' }
c.set_headers(headers)

#*args: url params, **kwargs: POST body
c.api.stream.read('quant.test.a', include_start=False)
```

