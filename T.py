import multiprocessing.pool
import threading
import multiprocessing

def foo(arg):
    print(arg)


t1 = threading.Thread(target=foo, args=("hello",))
t2 = threading.Thread(target=foo, args=("world",))

t1.start()
t2.start()
t1.join()
t2.join()

with multiprocessing.pool.ThreadPool(processes=2) as pool:
    pool.map(foo, ["hello", "world"])