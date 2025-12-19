import time
import threading
import asyncio

async def wait_operation(s):
    time.sleep(s)
    print("Terminado...")
    if s == 10:
        raise "Error"
    return 0



async def run_with_async():
    total_start = time.time()
    print("Haciendo proceso asincrono muy demorado")
    asyncio.create_task(wait_operation(10))
    result = await wait_operation(4)
    total_time = time.time() - total_start
    print(f"He terminado todas las tareas y he tardado {total_time}")
    ans = {"status":200 , "result": result}
    print(f"El resultado que me importa es {ans}")

def main():
    asyncio.run(run_with_async())
    
main()