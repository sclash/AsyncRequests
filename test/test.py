from AsyncRequests import AsyncHTTP 
from time import perf_counter
from RequestsType import RequestType
from RequestObject import RequestObject
from dataclasses import asdict

from time import perf_counter


api = 'https://api.publicapis.org/entries'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


endpoints = [RequestObject(url = api, params = {"title":"cat"}),
             RequestObject(url = api, params = {"title":"dog"}),
             RequestObject(url = api, params = {"title":"house"}),
             RequestObject(url = api, params = {"title":"weath"}),
             RequestObject(url = api, params = {"title":"py"})]

a = AsyncHTTP(
    url = endpoints,
    N_PRODUCERS=5,
    N_CONSUMERS=5
)

def get_json(r):
    return r.json()

start = perf_counter()
a.async_request(
    request_type= RequestType.GET,
    callback=get_json,
    headers = headers
)
print(a.response)
end = perf_counter()
print(f"Async EXECUTION TIME: {end-start}")



import requests

start = perf_counter()

res = []
for e in endpoints:
    res.append(requests.get(e.url,params = e.params, headers = headers).json()) 

end = perf_counter()
print(f"Sync EXECUTION TIME: {end-start}")