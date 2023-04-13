import requests
import asyncio

from helper import split_chunk

from typing import List, Callable, Optional

from RequestsType import RequestType

class AsyncRequests:
    url:List[str]
    queue: asyncio.Queue()
    N_PRODUCERS: int
    N_CONSUMERS: int
    response: List[requests.Response]

    def __init__(self, url: List[str], 
                request_type:RequestType = None,
                N_PRODUCERS: Optional[int] = 50,
                N_CONSUMERS: Optional[int] = 50):
        self.url = url
        self.request_type = request_type
        self.queue = asyncio.Queue()
        self.N_PRODUCERS = N_PRODUCERS
        self.N_CONSUMERS = N_CONSUMERS
        self.url_chunk = split_chunk(self.url, self.N_PRODUCERS)
        self.response = []

    def sync_http(self, url:str, **kwargs):
        try:
            r = self.request_type(url, **kwargs)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"Request exception: {e}")
            return r.status_code
    
    async def __async_http_thread(self, url: str, **kwargs):
        return await asyncio.to_thread(self.sync_http, url, **kwargs)
    
    async def __produce(self, chunk: List[str], **kwargs):
        try:
            for url in chunk:
                r = await self.__async_http_thread(url, **kwargs)
                await self.queue.put(r)
        except Exception as e:
            print(e)

    async def __consume(self, callback: Optional[Callable] = None):
        while True:
            try:
                data = await self.queue.get()
                if data is not None:
                    if callback != None:
                        self.response.append(callback(data))
                    else:
                        self.response.append(data)
                    self.queue.task_done()
            except Exception as e:
                print(f"CONSUMER ERRRO: {e}")
                self.queue.task_done()
                pass

    async def __run(self,callback: Optional[Callable] = None, **kwargs):
        producers = [asyncio.create_task(self.__produce(chunk, **kwargs)) for chunk in self.url_chunk]
        asyncio.gather(*producers)
        consumers = [asyncio.create_task(self.__consume(callback)) for i in range(self.N_CONSUMERS)]
        await asyncio.gather(*producers)
        
        await self.queue.join()
        for c in consumers:
            c.cancel()


class AsyncHTTP(AsyncRequests):

    def __init__(self, url: List[str], N_PRODUCERS, N_CONSUMERS):
        super().__init__(url, N_PRODUCERS, N_CONSUMERS)

    
    def async_request(self, 
                      request_type: RequestType,
                      callback: Optional[Callable] = None,
                      **kwargs):
        self.request_type = request_type
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))

    
    def async_get(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.GET
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))

    def async_post(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.POST
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))
    
    def async_put(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.PUT
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))

    def async_patch(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.PATCH
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))
    
    def async_delete(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.DELETE
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))