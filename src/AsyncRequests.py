import requests
import asyncio

from helper import split_chunk

from typing import List, Callable, Optional

from RequestsType import RequestType
from RequestObject import RequestObject
from dataclasses import asdict


import logging

import progressbar

from concurrent.futures import ThreadPoolExecutor
import os


c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s', datefmt= '%d-%m-%Y %H:%M:%S')
c_handler.setFormatter(c_format)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(c_handler)


global widgets 
widgets = [' [',
        progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
        '] ',
        progressbar.Bar('*'),' (',
        progressbar.ETA(), ') ',
        ]


# global queue 
# queue = asyncio.Queue()

class AsyncRequests:

    url:List[RequestObject]
    queue: asyncio.Queue
    N_PRODUCERS: int
    N_CONSUMERS: int
    response: List[requests.Response]

    def __init__(self, url: List[RequestObject], 
                request_type: Optional[RequestType] = None,
                N_PRODUCERS: int = 10,
                N_CONSUMERS: int = 10):
        self.url = url
        self.request_type = request_type
        self.queue = asyncio.Queue()
        self.N_PRODUCERS = N_PRODUCERS
        self.N_CONSUMERS = N_CONSUMERS
        self.url_chunk = split_chunk(self.url, self.N_PRODUCERS)
        self.response = []
        self.error_response = []
        self.bar_idx = 0
        self.bar = progressbar.ProgressBar(max_value=len(self.url), widgets=widgets).start()

    def sync_http(self, r_obj: RequestObject, session: requests.Session, **fixed_kwargs):
        try:
            url = r_obj.url
            var_kwargs = {k: asdict(r_obj)[k] for k in asdict(r_obj).keys() if k != 'url' and asdict(r_obj)[k]!=None} 
            kwargs = var_kwargs | fixed_kwargs
            if self.request_type:
                r = self.request_type(url, session, **kwargs)
                r_obj.status = r.status_code
                r.raise_for_status()
                return r
        except requests.exceptions.HTTPError as e_http:
            r_obj.status = e_http.response.status_code
            r_obj.request_error = e_http.__class__().__repr__()
            self.error_response.append((r_obj) )
            logger.error(f"Request ERROR for {r_obj.url}: {e_http}")
        except requests.exceptions.ConnectionError as e_conn:
            r_obj.request_error = e_conn.__class__().__repr__()
            self.error_response.append((r_obj))
            logger.error(f"Request ERROR for {r_obj.url}: {e_conn}")

    
    async def __async_http_thread(self, r_obj: RequestObject, session: requests.Session, **fixed_kwargs):
        return await asyncio.to_thread(self.sync_http, r_obj , session,  **fixed_kwargs)
    
    async def __produce(self, thread_name: int, aio_queue: asyncio.Queue, chunk: List[RequestObject], **fixed_kwargs):
        try:
            with requests.Session() as session:
                for r_obj in chunk:
                    r = await self.__async_http_thread(r_obj, session, **fixed_kwargs)
                    self.bar_idx += 1
                    self.bar.update(self.bar_idx)
                    if r:
                        await aio_queue.put(r)
                        if r_obj.url in [r_err.url for r_err in self.error_response]:
                            try:
                                self.error_response.remove(r_obj)
                            except Exception as e :
                                logger.error(f"PRODUCER ERROR at : {r_obj} | {e} - Thread {thread_name}")
                    else:
                        # await self.queue.put(None)
                        await aio_queue.put(None)
        except Exception as e:
            logger.error(f"PRODUCER ERROR: {chunk} | {e} - Thread {thread_name}")

    async def __consume(self, thread_name: int, aio_queue: asyncio.Queue, callback: Optional[Callable] = None):
        while True:
            try:
                # data = await self.queue.get()
                data = await aio_queue.get()
                if data is not None:
                    if callback != None:
                        self.response.append(callback(data))
                    else:
                        self.response.append(data)
                else:
                    logger.warning(f"DATA is NONE - Thread {thread_name}")
                # self.queue.task_done()
                aio_queue.task_done()
            except Exception as e:
                logger.error(f"CONSUMER ERROR: {e} - Thread {thread_name}")
                aio_queue.task_done()
                pass


    async def __run(self,url_chunk:List[RequestObject], thread_name: int, callback: Optional[Callable] = None, max_retries: int = 0, **fixed_kwargs):
        logger.info(f"Thread: {thread_name}")
        aio_queue = asyncio.Queue()
        print(url_chunk)
        producers = [asyncio.create_task(self.__produce(thread_name, aio_queue, [ chunk ], **fixed_kwargs)) for chunk in url_chunk]
        consumers = [asyncio.create_task(self.__consume(thread_name, aio_queue, callback)) for _ in range(self.N_CONSUMERS)]
        await asyncio.gather(*producers)
        
        # await self.queue.join()
        await aio_queue.join()
        for c in consumers:
            c.cancel()

        if len(self.error_response) > 0:
            if max_retries >0:
                errors = [{k:v for k,v in asdict(req).items() if k!= 'status' and k!='request_error'} for req in self.error_response]
                errors_req = [RequestObject(**err) for err in errors]
                error_chunk = split_chunk(errors_req, self.N_PRODUCERS)
                for i in range(max_retries):
                    if len(self.url) > len(self.response):
                        self.bar.max_value += len(self.error_response)
                        logger.info(f"{i+1}# RETRY / {max_retries}")
                        producers = [asyncio.create_task(self.__produce(thread_name, aio_queue, chunk, **fixed_kwargs)) for chunk in error_chunk]
                        consumers = [asyncio.create_task(self.__consume(thread_name, aio_queue, callback)) for _ in range(self.N_CONSUMERS)]
                        await asyncio.gather(*producers)
                        
                        # await self.queue.join()
                        await aio_queue.join()
                        for c in consumers:
                            c.cancel()

                

class AsyncHTTP(AsyncRequests):

    def __init__(self,  url: List[RequestObject], N_PRODUCERS = 10, N_CONSUMERS = 10):
        super().__init__(url, None, N_PRODUCERS, N_CONSUMERS)

    
    def async_request(self,
                      multithreaded: bool,
                      request_type: Callable,
                      callback: Optional[Callable] = None,
                      max_retries = 0,
                      **kwargs):
        self.request_type = request_type
        print(self.url)
        url_chunk = split_chunk(self.url, os.cpu_count())
        print(url_chunk)
        if multithreaded:
            workers = os.cpu_count()
            if workers:
                logger.info(f"multithreaded |  {workers} workers")
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    url_chunk = split_chunk(self.url, workers)
                    for i,chunk in enumerate(url_chunk):
                        print(chunk)
                        executor.submit(lambda: asyncio.run(self._AsyncRequests__run( chunk, i, callback, max_retries, **kwargs)))
        else:
            asyncio.run(self._AsyncRequests__run( self.url, 1, callback, max_retries, **kwargs))

    
    def async_get(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        self.request_type = RequestType.GET
        asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs))

    def async_post(self, callback: Optional[Callable] = None, max_retries = 0 ,**kwargs):
        self.request_type = RequestType.POST
        asyncio.run(self._AsyncRequests__run(callback,  max_retries, **kwargs))
    
    def async_put(self, callback: Optional[Callable] = None,  max_retries = 0, **kwargs):
        self.request_type = RequestType.PUT
        asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs))

    def async_patch(self, callback: Optional[Callable] = None, max_retries = 0,**kwargs):
        self.request_type = RequestType.PATCH
        asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs))
    
    def async_delete(self, callback: Optional[Callable] = None, max_retries = 0,**kwargs):
        self.request_type = RequestType.DELETE
        asyncio.run(self._AsyncRequests__run(callback,  max_retries, **kwargs))

    def async_head(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        self.request_type = RequestType.HEAD
        asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs))


# if __name__ == "__main__":
#
#     from time import perf_counter
#     BRANCH = "free-thread"
#     N_REQUESTS = 10
#     url = [RequestObject(url = "https://mockhttp.org") for _ in range(N_REQUESTS)]
#     print(split_chunk(url, os.cpu_count()))
#     print(len( split_chunk(url, os.cpu_count()) ))
#
#     q = asyncio.Queue()
#     print(hex( id(q) ))
#     start = perf_counter()
#     a = AsyncHTTP(url = url)
#     a.async_request(
#         request_type=RequestType.GET,
#         multithreaded=True,
#     )
#     end = perf_counter()
#
#     print(a.response)
#     print(len( a.response ))
#     print(len( a.error_response ))
#
#     print(BRANCH)
#     print(f"Time elapsed for {N_REQUESTS}: {end-start}")
#     print(hex( id(q) ))
