import requests 
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests_oauthlib import OAuth1, OAuth2
from dataclasses import dataclass, asdict

@dataclass
class RequestObject:
    url: str
    params:dict =None
    data:dict=None
    headers:dict=None
    cookies:dict=None
    files:dict=None
    auth:tuple | HTTPBasicAuth | HTTPProxyAuth | HTTPBasicAuth | OAuth1 | OAuth2=None
    timeout:float | tuple=None
    allow_redirects:bool=True
    proxies:dict = None 
    hooks:dict=None
    stream:bool=None
    verify:bool = True
    cert:str | tuple = None
    json:dict=None
