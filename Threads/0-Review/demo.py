import threading
import time
import random 

class Operation:
    
    def __init__(self,elements):
        self.elements = elements
    
    def operate(self, f, results, message="No estoy en un thread"):
        print("Start",message)
        ans = f(self.elements)
        results.append(ans) 
    

op = Operation([1,2,4,5,6]*100000)

def my_custom_fn(l):
    time.sleep(5)
    return f"Tarea realizada a {len(l)} elementos ..."


results = []

start_time = time.time()  

threads = []

for i in range(0,3000):
    t= threading.Thread(target=op.operate, args=(my_custom_fn, results))
    threads.append(t)
    
for t in threads:
    t.start()
    print("Inicie un thread..")
    
for t in threads:
    t.join()
    print("Espero un thread..")

print(f"Head resultados .. {len(results[:3])}")
duration = time.time() - start_time
print(f"La operacion duró : {duration}")