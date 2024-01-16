from AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
from dataclasses import asdict

api = 'https://api.publicapis.org/entries'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


<<<<<<< HEAD
=======

# 5 requests should be succesfull and 3 not

>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
endpoints = [RequestObject(url = api, params = {"title":"cat"}),
             RequestObject(url = api, params = {"title":"dog"}),
             RequestObject(url = 'http://fnkudshgjdfjgbfdk.com/', params = {"title":"fkhsudh"}), # should return an error
             RequestObject(url = api, params = {"title":"house"}),
             RequestObject(url = api, params = {"title":"weath"}),
             RequestObject(url = 'http://fnkudshgjdfjgbfdk.com/', params = {"title":"nfusdhif"}), #should return an error
<<<<<<< HEAD
             RequestObject(url = api, params = {"title":"py"})]
=======
             RequestObject(url = api, params = {"title":"py"}),
             RequestObject(url = 'https://httpbin.org/get/status/404')] 
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
             

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
<<<<<<< HEAD
=======
    max_retries=5,
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
    callback=get_json,
    headers = headers, 
    timeout = 5
)
# print(a.response)
end = perf_counter()
print(f"Async EXECUTION TIME: {end-start}")

len(a.response)
<<<<<<< HEAD
len(a.error_data)

=======
a.error_data # 3 of the original requests were unsuccessfull
len(a.error_response) # 18 tries 3 when it first runs. 3 more for 5 (max_retries) more times



######### SYNC EXAMPLE
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)
import requests

start = perf_counter()

res = []
for e in endpoints:
    res.append(requests.get(e.url,params = e.params, headers = headers).json()) 

end = perf_counter()
print(f"Sync EXECUTION TIME: {end-start}")

<<<<<<< HEAD
len(a.response)
=======
>>>>>>> 5996166 (performance imporvement - unsuccessful requests handling - progressbar tracking)



requests.get(url = api , params = {"tile":"sdvdfssf"})



# import pandas as pd
# from dataclasses import asdict
err = a.error_response
# df = pd.DataFrame()
# asdict(err[0][0])