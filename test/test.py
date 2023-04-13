from AsyncRequests import AsyncHTTP 
from time import perf_counter
from RequestsType import RequestType


url = ['https://google.com' for i in range(50)]
a = AsyncHTTP(url = url, N_PRODUCERS =10, N_CONSUMERS=10)
a.queue
a.url_chunk
# a.n_producers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}




start = perf_counter()
def example_callback(r):
    return r.status_code
a.async_request(
    request_type=RequestType.GET,
    callback = example_callback,
    headers = headers
)
# a.async_get(headers = headers, callback = example_callback)
end = perf_counter()
print(f"Async EXEC TIME: {end-start}")
print(a.response)

import requests 
start = perf_counter()
requests.get(url = url[0], headers = headers)
r = []
for i in url:
    r.append(requests.get(i).status_code)

end = perf_counter()
print(f"Sync EXEC TIME: {end-start}")
print(r)
