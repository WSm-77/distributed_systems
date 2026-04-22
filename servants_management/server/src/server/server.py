import sys
import traceback
import sys, traceback, Ice

from typing import List
from servants.counter_impl import CounterImpl
from servants.intwrapper_impl import IntWrapperObjectImpl

class Server:
    def __init__(self):
        self.counter = CounterImpl()
        self.int_wrapper = IntWrapperObjectImpl()

    def run(self, args: List[str] | None = None):
        status = 0
        ic = None
        try:
            ic = Ice.initialize(args)
            adapter = ic.createObjectAdapterWithEndpoints("SimplePrinterAdapter", "default -p 10000")
            adapter.add(self.counter, ic.stringToIdentity("Counter"))
            adapter.add(self.int_wrapper, ic.stringToIdentity("IntWrapper"))
            adapter.activate()
            ic.waitForShutdown()
        except:
            traceback.print_exc()
            status = 1

        if ic:
            try:
                ic.destroy()
            except:
                traceback.print_exc()
                status = 1

        sys.exit(status)


def app():
    srv = Server()
    srv.run()
