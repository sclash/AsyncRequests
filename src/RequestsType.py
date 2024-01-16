
from enum import Enum
import requests

class RequestType(Enum):
    GET = lambda url, session, **kwargs: session.get(url, **kwargs)
    POST = lambda url, session, **kwargs: session.post(url, **kwargs)
    PUT = lambda url, session, **kwargs: session.put(url, **kwargs)
    PATCH = lambda url, session, **kwargs: session.patch(url, **kwargs)
    DELETE = lambda url, session, **kwargs: session.delete(url, **kwargs)
    HEAD = lambda url, session, **kwargs: session.head(url, **kwargs)

