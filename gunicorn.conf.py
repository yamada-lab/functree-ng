import multiprocessing
bind = '0.0.0.0:8000'
threads = multiprocessing.cpu_count() * 2 + 1
