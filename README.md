# Async Requests

Python library to handle asynchronous http requests, built on top of the [requests](https://requests.readthedocs.io/en/latest/) library 


- [Installation](#installation)
- [Usage](#usage)

## Installation

[PyPI page](https://pypi.org/project/async-http-requests/)

```bash
pip install async-http-requests
```

## Usage

<<<<<<< HEAD
The library provide support for asynchronous http request, using the consumer-producer pattern.

Instantiate the class `AsyncHTTP` specifying a list of `RequestObject`, (you can specify `N_PRODUCERS` and `N_CONSUMERS`: default values are `50` for both)
=======
The library provide support for asynchronous http requests, using the consumer-producer pattern leveraging the built-in python modu.

Instantiate the class `AsyncHTTP` specifying a list of `RequestObject`, (you can specify `N_PRODUCERS` and `N_CONSUMERS`: default values are `10` for both)
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)

The `RequestObject` supports all keyword arguments of the requests methods (`headers`,`params`,`data`, ...). It allows you to specify different keyword arguments across different requests 

```python
from AysncRequests import AsyncHTPP, RequestObject, RequestType,

# Public API endpoint, it retrieves all public APIs listed under params specification
# Refer to this if you want to know more https://api.publicapis.org/
api = 'https://api.publicapis.org/entries'

<<<<<<< HEAD
# default N_PRODUCERS and N_CONSUMERS to 50 
=======
# default N_PRODUCERS and N_CONSUMERS to 10
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)

endpoints = [
    RequestObject(url = api, params = {"title":"cat"}),
    RequestObject(url = api, params = {"title":"dog"})
]

requests = AsyncHTTP(
    url = endpoints
) 


# specify number of producers and consumers

requests = AsyncHTTP(
    url = endpoints,
    N_PRODUCERS = 10,
    N_CONSUMERS = 10
)
```

To get the responses you can either call the generic `async_request` method explicitly specifying the http request type by passing to the `request_type` argument a `RequestType` Enum (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`),
<<<<<<< HEAD
or you can use the `async_get`, `async_post`, `async_delete`,`async_put`, `async_patch`, `async_head` method without having to spepcify the request type.
=======
or you can use the `async_get`, `async_post`, `async_delete`, `async_put`, `async_patch`, `async_head` method without having to spepcify the request type.
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)

```python
requests.async_request(
    request_type=RequestType.GET,
)

requests.async_get()

```

All methods support additional fixed keyword arguments such as `headers`, `auth` etc. as per the usual requests module, in case you need certain arguments to stay fixed across requests 

For the additional paramaters refer to the requests module documentation [Requests docs](https://requests.readthedocs.io/en/latest/)

```python
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'} # Keyword arguments FIXED for all requests

# Specify the RequestType

requests.async_request(
    request_type=RequestType.GET,
<<<<<<< HEAD
    haeders = headers 
=======
    haeders = headers # using the same header across all the requests
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
)

# Using async_get

<<<<<<< HEAD
requests.async_get(headers = headers)
```

All methods support the use callback functions, to be used by the consumers on the `request.Response` object generated by the producers, as they become available in the `asyncio.Queue`
=======
requests.async_get(headers = headers)  # using the same header across all the requests
```

All methods support the use of callback functions, to be used by the consumers on the `request.Response` object generated by the producers, as they become available in the `asyncio.Queue`.

In case of unsuccessfull requests the parameter `max_retries` can be specified (default is 0). 
When `max retries` is set larger than zero, any http request that has returned an error will be sent again up to the specified number of times if not successfull.
If the given requests still generates problems after all the attempts it will be pushed to the `requests.error_response` and won't be found in `requests.response`


The `max_retries` paramater can be useful when you are sending a big number of requests to the same server, in which case you can get an error just momentarily even if nothing is really wrong.
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)

```python
def example_callaback(response: request.Response):
    return response.status_code 


requests.async_request(
    request_type=RequestType.GET,
<<<<<<< HEAD
=======
    max_retries = 5,  # retry sendign the requests 5 times for all the unsuccessfull ones
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
    callback = example_callback,
    headers = headers
)

<<<<<<< HEAD
requests.async_get(
            headers = headers 
            callback = example_callback
=======

# no retries specified -> defaults to no further attempts in case of errors
requests.async_get(
            headers = headers,
            callback = lambda x: x.json() # lambda as callback
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
)

```

<<<<<<< HEAD
The results will be stored in a list object, where you'll find either the `requests.Response` objects, or the output of the `callback` function.
Requests that return an error code will be saved in `requests.error_response`
=======
- The results will be stored in a list object, where you'll find either the `requests.Response` objects, or the output of the `callback` function.
- Requests that return an error code will be saved in `requests.error_response`
- A summary of all the requests that were not successfull (if any) can be displayed summarized in a `pandas.DataFrame` object through the `requests.error_data` attribute
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)

```python 
requests.response
requests.error_response
<<<<<<< HEAD
=======
requests.error_data
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
```

Check the `test.py` script for an example.