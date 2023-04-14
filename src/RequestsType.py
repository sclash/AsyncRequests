
from enum import Enum
import requests

class RequestType(Enum):
    GET = lambda url,**kwargs: requests.get(url, **kwargs)
    POST = lambda url,**kwargs: requests.post(url, **kwargs)
    PUT = lambda url,**kwargs: requests.put(url, **kwargs)
    PATCH = lambda url,**kwargs: requests.patch(url, **kwargs)
    DELETE = lambda url,**kwargs: requests.delete(url, **kwargs)
    HEAD = lambda url,**kwargs: requests.head(url, **kwargs)




# RequestType.GET('https://google.com')