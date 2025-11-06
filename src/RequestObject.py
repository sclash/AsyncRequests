from requests.auth import HTTPBasicAuth, HTTPProxyAuth 
from requests_oauthlib import OAuth1, OAuth2
from dataclasses import dataclass

@dataclass
class RequestObject:
    url: str
    params:dict |None =None
    data:dict| None=None
    headers:dict | None=None
    cookies:dict | None =None
    files:dict | None=None
    auth:tuple | HTTPBasicAuth | HTTPProxyAuth | HTTPBasicAuth | OAuth1 | OAuth2 | None = None
    timeout:float | tuple | None =None
    allow_redirects:bool =True
    proxies:dict |None = None 
    hooks:dict |None=None
    stream:bool | None=None
    verify:bool |None = True
    cert:str | None = None
    json:dict | None=None
    status: int | None= None
    request_error: str | None = None
