
from enum import Enum
import requests

class RequestType(Enum):
    GET = lambda url, session, **kwargs: session.get(url, **kwargs)
    POST = lambda url, session, **kwargs: session.post(url, **kwargs)
    PUT = lambda url, session, **kwargs: session.put(url, **kwargs)
    PATCH = lambda url, session, **kwargs: session.patch(url, **kwargs)
    DELETE = lambda url, session, **kwargs: session.delete(url, **kwargs)
    HEAD = lambda url, session, **kwargs: session.head(url, **kwargs)
    OPTIONS = lambda url, session, **kwargs: session.options(url, **kwargs)

    def __call__(self, url: str, session: requests.Session, **kwargs):
        return self(url, session, **kwargs)

class RequestType_v1(Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5
    HEAD = 6
    OPTIONS = 7

    def __call__(self, url: str, session: requests.Session, **kwargs):
        match self:
            case RequestType_v1.GET:
                print(f"GET: {url}")
        return self(url, session, **kwargs)


def foo():
    ...


if __name__ == '__main__':
    rt_get = RequestType.GET
    rt_get_v1 = RequestType_v1.GET
    print(rt_get)
    print(type(rt_get))
    print(rt_get_v1)
    print(type(rt_get_v1))
    print(foo)
    print(type( foo ))
    with requests.Session() as sess:
        r = RequestType.GET(url = "https://google.com", session = sess)
        print(r)
    # with requests.Session() as sess_v1:
    #     r = RequestType_v1.GET(url = "https://google.com", session = sess_v1)
    #     print(r)
