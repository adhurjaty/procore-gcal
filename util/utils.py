from multiprocessing import Process
from threading import Lock
from urllib.parse import urlparse, urlencode, urlunparse


def parallel_for(fn, arg_list):
    lock = Lock()
    out_list = []

    def return_proc(arg):
        value = fn(arg)
        with lock:
            out_list.append(value)

    def start_proc(arg):
        p = Process(target=return_proc(arg))
        p.start()
        return p

    procs = [start_proc(arg) for arg in arg_list]
    for p in procs:
        p.join()

    return out_list


def build_url(base_url: str, path: str, args_dict: dict) -> str:
    url_parts = list(urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urlencode(args_dict)
    return urlunparse(url_parts)

