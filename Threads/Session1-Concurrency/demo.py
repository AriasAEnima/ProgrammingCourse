import threading
import time

class Operation:
    
    def __init__(self,elements):
        self.elements = elements
    
    def operate(self, f,message="No estoy en un thread"):
        print(message)
        return f(self.elements)
    

op = Operation([1,2,4,5,6]*100000)
op2 = Operation([-1,-2,-3,-4]*100000)


def complex_operation(l):
    ans = 1
    for e in l:
        ans = ans* e
    return ans

total_start = time.time()

#Normal process

#op.operate(complex_operation)
#op2.operate(complex_operation)

#VS Thread

my_thread = threading.Thread(target=op.operate,
                            args=(complex_operation,"Estoy el thread 1"))
my_thread.start()

total_time = time.time() - total_start
print(f"He terminado y he tardado {total_time}")
