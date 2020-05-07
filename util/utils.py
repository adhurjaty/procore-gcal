from multiprocessing import Process


def parallel_for(fn, arg_list):
    procs = [Process(target=fn(arg)) for arg in arg_list]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
