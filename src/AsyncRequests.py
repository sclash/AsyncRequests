import asyncio
import os
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from typing import List, Callable, Optional
from dataclasses import asdict
import logging

import requests
import progressbar

from helper import split_chunk
from RequestsType import RequestType
from RequestObject import RequestObject


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


class _AsyncRequests:

    url:List[RequestObject]
    N_PRODUCERS: int
    N_CONSUMERS: int
    response: List[requests.Response]

    def __init__(self, url: List[RequestObject], 
                request_type: Optional[RequestType] = None,
                N_PRODUCERS: int = 10,
                N_CONSUMERS: int = 10):
        self.url = url
        self.request_type = request_type
        self.N_PRODUCERS = N_PRODUCERS
        self.N_CONSUMERS = N_CONSUMERS
        self.url_chunk = split_chunk(self.url, self.N_PRODUCERS)
        self.response = []
        self.error_response = []
        self.bar_idx = 0
        self.bar = progressbar.ProgressBar(maxval=len(self.url), widgets=widgets).start()
        self.lock = Lock()

    def sync_http(self, r_obj: RequestObject, session: requests.Session, **fixed_kwargs):
        try:
            url = r_obj.url
            var_kwargs = {k: asdict(r_obj)[k] for k in asdict(r_obj).keys() 
                               if k != 'url' and asdict(r_obj)[k]!=None and k != 'status'} 
            kwargs = var_kwargs | fixed_kwargs
            if self.request_type:
                r = self.request_type(url, session, **kwargs)
                r_obj.status = r.status_code
                r.raise_for_status()
                return r
        except requests.exceptions.HTTPError as e_http:
            r_obj.status = e_http.response.status_code
            r_obj.request_error = e_http.__class__().__repr__()
            with self.lock:
                self.error_response.append((r_obj) )
            logger.error(f"Request ERROR for {r_obj.url}: {e_http}")
        except requests.exceptions.ConnectionError as e_conn:
            r_obj.request_error = e_conn.__class__().__repr__()
            with self.lock:
                self.error_response.append((r_obj))
            logger.error(f"Request ERROR for {r_obj.url}: {e_conn}")

    
    async def __async_http_thread(self, 
                                  r_obj: RequestObject,
                                  session: requests.Session, 
                                  **fixed_kwargs):
        return await asyncio.to_thread(self.sync_http, 
                                       r_obj, 
                                       session,
                                       **fixed_kwargs)
    
    async def __produce(self, 
                        thread_name: int,
                        aio_queue: asyncio.Queue,
                        chunk: List[RequestObject],
                        **fixed_kwargs):
        try:
            with requests.Session() as session:
                for r_obj in chunk:
                    r = await self.__async_http_thread(r_obj, session, **fixed_kwargs)
                    with self.lock:
                        self.bar_idx += 1
                        self.bar.update(self.bar_idx)
                    if r:
                        await aio_queue.put(r)
                        if r_obj.url in [r_err.url for r_err in self.error_response]:
                            try:
                                with self.lock:
                                    self.error_response.remove(r_obj)
                            except Exception as e :
                                logger.error(f"PRODUCER ERROR at : {r_obj} | {e} - Thread {thread_name}")
                    else:
                        await aio_queue.put(None)
        except Exception as e:
            logger.error(f"PRODUCER ERROR: {chunk} | {e} - Thread {thread_name}")

    async def __consume(self,
                        thread_name: int, 
                        aio_queue: asyncio.Queue,
                        callback: Optional[Callable] = None):
        while True:
            try:
                data = await aio_queue.get()
                with self.lock:
                    if data is not None:
                        if callback != None:
                                self.response.append(callback(data))
                        else:
                            self.response.append(data)
                    else:
                        logger.warning(f"DATA is NONE - Thread {thread_name}")
                aio_queue.task_done()
            except Exception as e:
                logger.error(f"CONSUMER ERROR: {e} - Thread {thread_name}")
                aio_queue.task_done()
                pass


    async def __run(self,
                    url_chunk:List[RequestObject],
                    thread_name: int,
                    callback: Optional[Callable] = None, 
                    max_retries: int = 0,
                    **fixed_kwargs):
        logger.info(f"Thread: {thread_name}")
        aio_queue = asyncio.Queue()
        print(url_chunk)
        producers = [asyncio.create_task(self.__produce(thread_name, aio_queue, [ chunk ], **fixed_kwargs)) for chunk in url_chunk]
        consumers = [asyncio.create_task(self.__consume(thread_name, aio_queue, callback)) for _ in range(self.N_CONSUMERS)]
        await asyncio.gather(*producers)
        
        await aio_queue.join()
        for c in consumers:
            c.cancel()

        if len(self.error_response) > 0:
            if max_retries >0:
                with self.lock:
                    errors = [{k:v for k,v in asdict(req).items() if k!= 'status' and k!='request_error'} 
                        for req in self.error_response]
                    errors_req = [RequestObject(**err) for err in errors]
                    error_chunk = split_chunk(errors_req, self.N_PRODUCERS)
                for i in range(max_retries):
                    if len(self.url) > len(self.response):
                        with self.lock:
                            self.bar.max_value += len(self.error_response)
                        logger.info(f"{i+1}# RETRY / {max_retries}")
                        producers = [asyncio.create_task(self.__produce(thread_name,
                                                                        aio_queue,
                                                                        chunk,
                                                                        **fixed_kwargs)) for chunk in error_chunk]
                        consumers = [asyncio.create_task(self.__consume(thread_name,
                                                                        aio_queue,
                                                                        callback)) for _ in range(self.N_CONSUMERS)]
                        await asyncio.gather(*producers)
                        
                        await aio_queue.join()
                        for c in consumers:
                            c.cancel()

                

class AsyncHTTP(_AsyncRequests):

    def __init__(self,  
                 url: List[RequestObject],
                 N_PRODUCERS = 10,
                 N_CONSUMERS = 10,
                 multithreaded: bool = False,
                 workers: Optional[int] = os.cpu_count()):
        super().__init__(url, None, N_PRODUCERS, N_CONSUMERS)
        self.multithreaded = multithreaded
        self.workers = workers

    
    def async_request(self,
                      request_type: Callable,
                      callback: Optional[Callable] = None,
                      max_retries = 0,
                      **kwargs):

        """
        request_type: RequstType.GET
        multithreaded: True if you want multiple threads
        workers: number of threads. Defaults to # of cpu_cores.
                If multithreaded is False is ignored
        callback: Callable function to process the response as they are received
        max_ retries: int. Default is 0. If any requests returns an Error you can retry,
                            max_retries times
        **kwargs: additional keyword arguments as per the requests module (ex. headers, etc.)
        """
        self.request_type = request_type
        url_chunk = split_chunk(self.url, os.cpu_count())
        if self.multithreaded:
            if self.workers:
                logger.info(f"multithreaded |  {self.workers} workers")
                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    url_chunk = split_chunk(self.url, self.workers)
                    for i,chunk in enumerate(url_chunk):
                        executor.submit(lambda: asyncio.run(self._AsyncRequests__run( chunk, i, callback, max_retries, **kwargs)))
        else:
            asyncio.run(self._AsyncRequests__run( self.url, 1, callback, max_retries, **kwargs))

    
    def async_get(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.GET,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )

    def async_post(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.POST,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )

    def async_put(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.PUT,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )

    def async_patch(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.PATCH,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )
    
    def async_delete(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.DELETE,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )

    def async_head(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.HEAD,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )

    def async_options(self, callback: Optional[Callable] = None, max_retries = 0, **kwargs):
        return self.async_request(
            request_type= RequestType.OPTIONS,
            callback= callback,
            max_retries = max_retries,
            **kwargs
        )
