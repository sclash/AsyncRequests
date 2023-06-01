from AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
from dataclasses import asdict

api = 'https://api.publicapis.org/entries'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


endpoints = [RequestObject(url = api, params = {"title":"cat"}),
             RequestObject(url = api, params = {"title":"dog"}),
             RequestObject(url = 'https://fuckweb.com/', params = {"title":"fica"}),
             RequestObject(url = api, params = {"title":"house"}),
             RequestObject(url = api, params = {"title":"weath"}),
             RequestObject(url = 'https://fuckweb.com/', params = {"title":"cazzo"}),
             RequestObject(url = api, params = {"title":"py"})]
             

a = AsyncHTTP(
    url = endpoints,
    N_PRODUCERS=5,
    N_CONSUMERS=5
)
len(a.url_chunk)
def get_json(r):
    return r.json()

start = perf_counter()
a.async_request(
    request_type= RequestType.GET,
    callback=get_json,
    headers = headers, 
    timeout = 5
)
# print(a.response)
end = perf_counter()
print(f"Async EXECUTION TIME: {end-start}")

len(a.response)
len(a.error_data)

import requests

start = perf_counter()

res = []
for e in endpoints:
    res.append(requests.get(e.url,params = e.params, headers = headers).json()) 

end = perf_counter()
print(f"Sync EXECUTION TIME: {end-start}")

len(a.response)



requests.get(url = api , params = {"tile":"cazzo"})



# import pandas as pd
# from dataclasses import asdict
err = a.error_response
# df = pd.DataFrame()
# asdict(err[0][0])