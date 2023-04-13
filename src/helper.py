
import json
from typing import Union, List
import datetime as dt


def split_chunk(l:list, N_PRODUCERS)->list:
    """
    split list in chunks to avoid too many threads
    """
    chunk = []
    x =  len(l)//N_PRODUCERS
    if x == 0:
        return [l]
    else:
        for i in range(N_PRODUCERS):
            if i < N_PRODUCERS-1:
                chunk.append(l[i*x:(i+1)*x])
            else:
                chunk.append(l[i*x:])
        return chunk