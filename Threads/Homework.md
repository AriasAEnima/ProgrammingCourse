# Homework

Por favor realiza 6 un experimentos de la siguiente manera:  

1. Simule un procedimiento de bloqueo con time.sleep() , que espere 1 segundo y produzca un log y despues un valor aleatorio entre 0 y 0.5 segundos de espera.

    1.1 Realice este procedimiento 20 veces de manera secuencial. Capture una imagen los resultados en de tiempo total del procedimiento

    2.2 Realice este procedimiento 20 veces usando ThreadPool con 10 workers. Capture una imagen los resultados en de tiempo total del procedimiento.

    2.3 Realice este procedimiento 20 veces usando ProcessPool con 10 workers. Capture una imagen los resultados en de tiempo total del procedimiento.
2. Calcular la suma de los factoriales de 1 a N, es decir 
   1! + 2! + 3! + ....  n! 
    
    2.1 Realice este procedimiento de 1 a 1000000 (o un numero mas grande que pueda comprobar diferencias notables) de manera secuencial. Capture una imagen los resultados en de tiempo total del procedimiento

    2.2 Realice este procedimiento usando un ThreadPool usando 4 rangos (Task A : [1 250000], Task B: [250001 5000000] .... ) con 4 workers. Capture una imagen los resultados en de tiempo total del procedimiento.
    
    2.3 Realice el mismo experimento del punto 2.2 usando ProcessPool.  Capture una imagen los resultados en de tiempo total del procedimiento.