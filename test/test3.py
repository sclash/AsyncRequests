from src.AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
import asyncio
# import pandas as pd
# df = pd.DataFrame()

BRANCH = "free-thread"
N_REQUESTS = 1000
url = [RequestObject(url = "https://mockhttp.org") for _ in range(N_REQUESTS)]


q = asyncio.Queue()
print(hex( id(q) ))
start = perf_counter()
a = AsyncHTTP(url = url)
a.async_request(
    request_type=RequestType.GET,
    multithreaded=True,
)
end = perf_counter()

print(a.response)
print(len( a.response ))
print(len( a.error_response ))

print(BRANCH)
print(f"Time elapsed for {N_REQUESTS}: {end-start}")
print(hex( id(q) ))
