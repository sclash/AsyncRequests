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
    
    async def __produce(self, chunk: List[RequestObject], **fixed_kwargs):
        try:
            with requests.Session() as session:
                for r_obj in chunk:
                    r = await self.__async_http_thread(r_obj, session, **fixed_kwargs)
                    self.bar_idx += 1
                    self.bar.update(self.bar_idx)
                    if r:
                        await self.queue.put(r)
                        if r_obj.url in [r_err.url for r_err in self.error_response]:
                            try:
                                self.error_response.remove(r_obj)
                            except Exception as e :
                                logger.error(f"PRODUCER ERROR at : {r_obj} | {e}")
                    else:
                        await self.queue.put(None)
        except Exception as e:
            logger.error(f"PRODUCER ERROR: {chunk} | {e}")

    async def __consume(self, callback: Optional[Callable] = None):
        while True:
            try:
                data = await self.queue.get()
                if data is not None:
                    if callback != None:
                        self.response.append(callback(data))
                    else:
                        self.response.append(data)
                else:
                    logger.warning(f"DATA is NONE")
                self.queue.task_done()
            except Exception as e:
                logger.error(f"CONSUMER ERROR: {e}")
                self.queue.task_done()
                pass


    async def __run(self,callback: Optional[Callable] = None, max_retries: int = 0, **fixed_kwargs):
        producers = [asyncio.create_task(self.__produce(chunk, **fixed_kwargs)) for chunk in self.url_chunk]
        consumers = [asyncio.create_task(self.__consume(callback)) for _ in range(self.N_CONSUMERS)]
        await asyncio.gather(*producers)
        
        await self.queue.join()
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
                        producers = [asyncio.create_task(self.__produce(chunk, **fixed_kwargs)) for chunk in error_chunk]
                        consumers = [asyncio.create_task(self.__consume(callback)) for _ in range(self.N_CONSUMERS)]
                        await asyncio.gather(*producers)
                        
                        await self.queue.join()
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
        if not multithreaded:
            asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs))
        else:
            workers = os.cpu_count()
            logger.info(f"multithreaded |  {workers} of workers")
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for _ in range(workers):
                    executor.submit(lambda: asyncio.run(self._AsyncRequests__run(callback, max_retries, **kwargs)))

    
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
