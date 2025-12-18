import threading
import time
import random 
class Operation:
    
    def __init__(self,elements):
        self.elements = elements
    
    def operate(self, f,message="No estoy en un thread"):
        print("Start",message)
        ans = f(self.elements)
        print("Finished task", message)
        return ans
    

op = Operation([1,2,4,5,6]*100000)
op2 = Operation([-1,-2,-3,-4]*100000)


def complex_operation(l):
    ans = 1
    for e in l:
        ans = ans* e
    return ans

def wait_operation(_):
    random_wait = random.randint(1,2)
    time.sleep(random_wait)
    return 0
    

total_start = time.time()

# Normal process
op.operate(complex_operation, "Operation 1")
op2.operate(wait_operation, "Operation 2")

total_time = time.time() - total_start
print(f"He terminado todas las tareas y he tardado {total_time}")
