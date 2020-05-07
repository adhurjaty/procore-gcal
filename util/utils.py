from multiprocessing import Process


def parallel_for(fn, arg_list):
    def start_proc(arg):
        p = Process(target=fn(arg))
        p.start()
        return p

    procs = [start_proc(arg) for arg in arg_list]
    for p in procs:
        p.join()
