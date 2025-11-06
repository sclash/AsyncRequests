from src.AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter

BRANCH = "free-thread"
N_REQUESTS = 3000
url = [RequestObject(url = "https://mockhttp.org") for _ in range(N_REQUESTS)]


start = perf_counter()
a = AsyncHTTP(url = url)
a.async_request(
    request_type=RequestType.GET,
    multithreaded=True,
    callback=lambda x : x,
    max_retries=5
)

end = perf_counter()

print(a.response)
print(len( a.response ))
print(len( a.error_response ))

print(BRANCH)
print(f"Time elapsed for {N_REQUESTS}: {end-start}")
