
from datetime import datetime

def crear_funcion_x_n(n):
    def my_function(x):
        return x * n
    return my_function


x_por_20 = crear_funcion_x_n(20)

print(x_por_20(2))

l = ["2","3","4","5","6","8"]

def transformar(l,f,g):
    return g(f(l))


def partial(f):
    def transformar_acortado(l,g):
        return g(f(l))
    
    return transformar_acortado


print(transformar(l,lambda x: map(int,x),lambda x: sum(x)/len(l)))
print(transformar(l,lambda x: map(int,x),lambda x: max(x)))

# Referencia a funcion que caster a int a primera intancia y 
# aplica una segunda funcion a la collecion
transformar_acortado = partial(lambda x: map(int,x))

print(transformar_acortado(l,lambda x: sum(x)/len(l)))
print(transformar_acortado(l,lambda x: max(x)))

def partial_args(*args):
    def transformar_argumentos(f):
        return f([*args])
    return transformar_argumentos


partial_args_l = partial_args(2,3,4,5,6,-2,1,10)

print(partial_args_l(sum))
print(partial_args_l(max))
print(partial_args_l(min))


print(partial_args_l.__name__)


def good_rename(f):
    def new_func(*args):
        return f([*args])
    return new_func


new_sum = good_rename(sum)

print(new_sum(1,3,55,6))

def decorador_flexible(*dec_args, **dec_kwargs):
    """Decorador que puede recibir argumentos opcionales."""
    print(f"🎭 Creando decorador con args: {dec_args}, kwargs: {dec_kwargs}")
    
    def decorador_real(func):
        def wrapper(*func_args, **func_kwargs):
            start_time = datetime.now()

            print(f"   Inicio de la función: {start_time}")
        
            resultado = func(*func_args, **func_kwargs)

            end_time = datetime.now()

            print(f"   Fin de la función: {end_time}")

            time_difference = end_time - start_time

            # Access components of the timedelta
            total_seconds = time_difference.total_seconds()

            print(f"  Time spend: {total_seconds}")

            return resultado
        return wrapper
    return decorador_real

@decorador_flexible()
def mi_funcion_1(n):
    ans = []
    for i in range(0,n):
        ans.append(i)


def mi_funcion_1(n):
    ans = []
    for i in range(0,n):
        ans.append(i)

        

print(mi_funcion_1(100000000))







