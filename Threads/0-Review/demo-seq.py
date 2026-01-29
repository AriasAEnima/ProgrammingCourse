import time

class Operation:
    def slow_operation(self):
        time.sleep(5)
        print("Llamado a la API terminó ...")

print(f"La operacion Empieza ...")

start_time = time.time()      
        
op = Operation()

for i in range(0,3):
    op.slow_operation()

duration = time.time() - start_time

print(f"La operacion duró : {duration}")