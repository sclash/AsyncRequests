from AsyncRequests import AsyncHTTP, RequestType, RequestObject
from time import perf_counter
from dataclasses import asdict


BASE_URL  ='https://httpbin.org/get'
# BASE_URL  ='http://faurghlsuihgsflgb.com'
# BASE_URL  ='https://httpbin.org/get/status/404'
import time 
N_REQUESTS = 10_000

def main_async_http():
    try:
        start_async_http = time.perf_counter()


        urls = [RequestObject(f"{BASE_URL}") for i in range(N_REQUESTS)]
        urls.append(RequestObject(url = 'https://httpbin.org/get/status/502'))
        # urls.append(RequestObject(url = 'https://httpbin.org/get/status/502'))


        a = AsyncHTTP(
            url = urls,
            # N_PRODUCERS=50,
            # N_CONSUMERS=50,
        )

        a.async_request(
            request_type=RequestType.GET,
            max_retries = 5,
            callback= lambda x: x.json()
        )

        # a.async_get(max_retries = 5, callback=lambda x: x.json())
        
        # assert len(a.response) == N_REQUESTS

        end_async_http = time.perf_counter()

        print(f"ASYNC-HTTP TIME TAKEN FOR {N_REQUESTS} HTTP REQUESTS: {end_async_http-start_async_http}")
        return a
    except Exception as e:
        print(f"ASYNC-HTTP FAILED: {e}")
        pass



# if __name__ == '__main__':
    # asyncio.run(main_httpx())
response = main_async_http()
print(len(response.response))
print(len(response.error_response))
response.error_response
if len(response.error_response) > 0:
    response.error_data

len(response.response)
len(response.error_response)



# [i.json()['url'] for i in response.response]

len(response.url)