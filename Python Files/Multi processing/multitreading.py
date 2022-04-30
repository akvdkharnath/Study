from threading import Thread
import multitreading

def squre(x):
    print(x * x)

if __name__ == "__main__":
    t1 = Thread(target=squre, args=(3,))
    t2 = Thread(target=squre, args=(4,))
    t1.start()
    t2.start()

