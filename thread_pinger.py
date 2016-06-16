import os
import multiprocessing
import subprocess

DNULL = open(os.devnull, 'w')
def ping(host,mp_queue):
    response = subprocess.call(["ping", "-c", "1", "-w", '2', host], stdout=DNULL)
    if response == 0:
        print host, 'is up!'
        result = True
    else:
        print host, 'is down!'
        result = False
    mp_queue.put((result,host))
 
def ping_ips(devices):
    mp_queue = multiprocessing.Queue()
    processes = []
    for device in devices:
        p = multiprocessing.Process(target=ping, args=(device, mp_queue))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    results = {True:[], False:[]}
    for p in processes:
        key, value =  mp_queue.get()
        results[key] += [value]
    return results[True]

