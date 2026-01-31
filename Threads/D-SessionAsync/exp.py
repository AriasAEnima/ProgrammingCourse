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
    # Proceso no fundamental pero muy demorado
    # con alta posibilidad de fallo
    asyncio.create_task(wait_operation(10))   # t = Thread() start() => 10s
    # vs wait_operation(10) <= WARNING async function running without catching
    # asyncio.create_task avoid WARNING paralelizado de manera consciente no voy a guardar ningun resultaod
    # create_task TIENE RETURN
    # proceso fundamental
    result = await wait_operation(4) # 4s = Thread() start() join()
    # await "cancela" el async
    total_time = time.time() - total_start
    print(f"He terminado todas las tareas y he tardado {total_time}")
    ans = {"status":200 , "result": result}
    print(f"El resultado que me importa es {ans}")

def main():
    asyncio.run(run_with_async()) # t = Thread() # start()
    
main()