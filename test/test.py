# from AsyncRequests import AsyncHTTP, RequestType, RequestObject
from src.AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
import sys

api = 'https://api.publicapis.org/entries'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


print("BRANCH: free-threading")


# 5 requests should be succesfull and 3 not

endpoints = [RequestObject(url = api, params = {"title":"cat"}),
             RequestObject(url = api, params = {"title":"dog"}),
             RequestObject(url = 'http://fnkudshgjdfjgbfdk.com/', params = {"title":"fkhsudh"}), # should return an error
             RequestObject(url = api, params = {"title":"house"}),
             RequestObject(url = api, params = {"title":"weath"}),
             RequestObject(url = 'http://fnkudshgjdfjgbfdk.com/', params = {"title":"nfusdhif"}), #should return an error
             RequestObject(url = api, params = {"title":"py"}),
             RequestObject(url = 'https://httpbin.org/get/status/404')] 
             

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
    max_retries=5,
    callback=get_json,
    headers = headers, 
    timeout = 5
)

# print(a.response)
end = perf_counter()
print(f"Async EXECUTION TIME: {end-start}")

print(len(a.response))
# print(a.error_data) # 3 of the original requests were unsuccessfull
print(len(a.error_response)) # 18 tries 3 when it first runs. 3 more for 5 (max_retries) more times
print(a.error_response)
print(sys._is_gil_enabled())



######### SYNC EXAMPLE
# import requests
#
# start = perf_counter()
#
# res = []
# for e in endpoints:
#     res.append(requests.get(e.url,params = e.params, headers = headers).json()) 
#
# end = perf_counter()
# print(f"Sync EXECUTION TIME: {end-start}")
#
#
#
#
# requests.get(url = api , params = {"tile":"sdvdfssf"})
#
#
#
# # import pandas as pd
# # from dataclasses import asdict
# err = a.error_response
# # df = pd.DataFrame()
# # asdict(err[0][0])
