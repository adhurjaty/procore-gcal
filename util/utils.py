from multiprocessing import Process
from urllib.parse import urlparse, urlencode, urlunparse


def parallel_for(fn, arg_list):
    def start_proc(arg):
        p = Process(target=fn(arg))
        p.start()
        return p

    procs = [start_proc(arg) for arg in arg_list]
    for p in procs:
        p.join()


def build_url(base_url: str, path: str, args_dict: dict) -> str:
    url_parts = list(urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urlencode(args_dict)
    return urlunparse(url_parts)

