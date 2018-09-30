import threading

class LogLockKeeper:
    lock = None

    @classmethod
    def getConsoleLock(cls):

        if not cls.lock:
            cls.lock = threading.RLock()

        return cls.lock


def doWork(msg):
    # with LogLockKeeper.getConsoleLock():
    #     print msg
    print msg



ta = threading.Thread(target= doWork, args= ('Thread a',))
tb = threading.Thread(target= doWork, args= ('Thread b',))
tc = threading.Thread(target= doWork, args= ('Thread c',))


ta.run()
tb.run()
tc.run()
