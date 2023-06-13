import requests
import asyncio

from helper import split_chunk

from typing import List, Callable, Optional

from RequestsType import RequestType
from RequestObject import RequestObject
from dataclasses import asdict
import pandas as pd

import logging

c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s', datefmt= '%d-%m-%Y %H:%M:%S')
c_handler.setFormatter(c_format)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(c_handler)

class AsyncRequests:
    url:List[str]
    queue: asyncio.Queue()
    N_PRODUCERS: int
    N_CONSUMERS: int
    response: List[requests.Response]

    def __init__(self, url: List[RequestObject], 
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
        self.error_response = []
        self.error_data: pd.DataFrame = None

    def sync_http(self, r_obj: RequestObject, **fixed_kwargs):
        try:
            url = r_obj.url
            var_kwargs = {k: asdict(r_obj)[k] for k in asdict(r_obj).keys() if k != 'url' and asdict(r_obj)[k]!=None} 
            # kwargs = {k: asdict(r_obj)[k] for k in asdict(r_obj).keys() if k != 'url'} | fixed_kwargs
            kwargs = var_kwargs | fixed_kwargs
            r = self.request_type(url, **kwargs)
            r.raise_for_status()
            logger.info(f"SUCCESSFULL Request for {r_obj.url} - {var_kwargs}")
            return r
        except Exception as e:
            # self.error_response.append((r_obj, r.status_code))
            self.error_response.append((r_obj) )

            logger.error(f"Request ERROR for {r_obj.url}: {e}")
            # return r.status_code
    
    async def __async_http_thread(self, r_obj: RequestObject, **fixed_kwargs):
        return await asyncio.to_thread(self.sync_http, r_obj , **fixed_kwargs)
    
    async def __produce(self, chunk: List[RequestObject], **fixed_kwargs):
        try:
            for r_obj in chunk:
                r = await self.__async_http_thread(r_obj, **fixed_kwargs)
                if r:
                    await self.queue.put(r)
                else:
                    await self.queue.put(None)
        except Exception as e:
            # self.error_response.append((r_obj, r.status_code))
            # self.error_response.append(asdict(r_obj)| {'status_code': r.status_code, 'response': r.text})
            self.error_response.append((r_obj))
            logger.error(f"PRODUCER ERROR: {r_obj}")
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
                else:
                    logger.warning(f"DATA is NONE")
                self.queue.task_done()
            except Exception as e:
                logger.errror(f"CONSUMER ERROR: {e}")
                self.queue.task_done()
                pass

    async def __run(self,callback: Optional[Callable] = None, **fixed_kwargs):
        producers = [asyncio.create_task(self.__produce(chunk, **fixed_kwargs)) for chunk in self.url_chunk]
        consumers = [asyncio.create_task(self.__consume(callback)) for i in range(self.N_CONSUMERS)]
        await asyncio.gather(*producers)
        
        await self.queue.join()
        for c in consumers:
            c.cancel()

        if len(self.error_response) > 0:
            self.error_data = pd.DataFrame()
            for idx, err in enumerate(self.error_response):
                self.error_data = pd.concat([self.error_data, pd.DataFrame(asdict(err), index = [idx]) ])
                

class AsyncHTTP(AsyncRequests):

    def __init__(self, url: List[RequestObject], N_PRODUCERS, N_CONSUMERS):
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

    def async_head(self, callback: Optional[Callable] = None,**kwargs):
        self.request_type = RequestType.HEAD
        asyncio.run(self._AsyncRequests__run(callback, **kwargs))