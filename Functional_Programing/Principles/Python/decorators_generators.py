"""
Decoradores y Generadores - Guía Simple y Clara
==================================================

Este archivo muestra de forma simple cómo funcionan los decoradores 
y generadores en programación funcional con ejemplos paso a paso.
"""

# =============================================================================
# PARTE 1: GENERADORES BÁSICOS - ¿Qué es y cómo funciona?
# =============================================================================

def simple_generator():
    """Generador básico que produce 3 números."""
    print("Generando número 1...")
    yield 1
    print("Generando número 2...")
    yield 2
    print("Generando número 3...")
    yield 3
    print("Generador terminado")


def numbers_generator(start, end):
    """Generador que produce números de start a end."""
    current = start
    while current <= end:
        print(f"Produciendo: {current}")
        yield current
        current += 1


def fibonacci_generator():
    """Generador infinito de Fibonacci - solo calcula cuando se pide."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# =============================================================================
# PARTE 2: DECORADORES BÁSICOS - ¿Qué es y cómo funciona?
# =============================================================================

def simple_decorator(func):
    """Decorador básico que añade funcionalidad a una función."""
    def wrapper(*args, **kwargs):
        print(f">>> Ejecutando función: {func.__name__}")
        result = func(*args, **kwargs)
        print(f">>> Resultado: {result}")
        return result
    return wrapper


def count_calls(func):
    """Decorador que cuenta cuántas veces se llama una función."""
    count = {'calls': 0}  # Usar diccionario para mantener referencia
    
    def wrapper(*args, **kwargs):
        count['calls'] += 1
        print(f"Llamada #{count['calls']} a {func.__name__}")
        result = func(*args, **kwargs)
        return result
    
    # Método para obtener el conteo actual
    wrapper.get_count = lambda: count['calls']
    
    return wrapper


# =============================================================================
# PARTE 3: EJEMPLOS PRÁCTICOS CON ENTRADA Y SALIDA CLARA
# =============================================================================

@count_calls
def suma(a, b):
    """Función simple que suma dos números."""
    return a + b


@simple_decorator  
def suma_decorada(a, b):
    """Función con decorador simple para mostrar ejecución."""
    return a + b


@count_calls
def fibonacci_tradicional(n):
    """Fibonacci tradicional - ineficiente."""
    if n <= 1:
        return n
    return fibonacci_tradicional(n-1) + fibonacci_tradicional(n-2)


def demostrar_generadores():
    """Demuestra paso a paso cómo funcionan los generadores."""
    print("🔹 DEMO: Generador Simple")
    print("=" * 40)
    
    # Crear el generador (no ejecuta código aún)
    gen = simple_generator()
    print(f"Generador creado: {gen}")
    print("Nota: Aún no se ha ejecutado código\n")
    
    # Usar el generador paso a paso
    print("Obteniendo valores uno por uno:")
    print(f"next(gen) = {next(gen)}")  # Ejecuta hasta el primer yield
    print(f"next(gen) = {next(gen)}")  # Ejecuta hasta el segundo yield
    print(f"next(gen) = {next(gen)}")  # Ejecuta hasta el tercer yield
    print()
    
    # Generador con parámetros
    print("🔹 DEMO: Generador con Parámetros")
    print("=" * 40)
    print("Creando generador de números del 5 al 8:")
    num_gen = numbers_generator(5, 8)
    
    print("Convirtiendo a lista (ejecuta todo el generador):")
    result = list(num_gen)
    print(f"Resultado: {result}")
    print()
    
    # Generador infinito con límite
    print("🔹 DEMO: Generador Infinito (Fibonacci)")
    print("=" * 40)
    print("Creando generador infinito de Fibonacci...")
    fib_gen = fibonacci_generator()
    
    print("Tomando solo los primeros 10 valores:")
    fibonacci_10 = []
    for i in range(10):
        fibonacci_10.append(next(fib_gen))
    
    print(f"Primeros 10 Fibonacci: {fibonacci_10}")
    print("Nota: El generador puede seguir produciendo más valores")
    print()


def demostrar_decoradores():
    """Demuestra paso a paso cómo funcionan los decoradores."""
    print("🔸 DEMO: Decoradores")
    print("=" * 40)
    
    print("1. Función con decorador de conteo:")
    print("Llamando suma(3, 5):")
    resultado = suma(3, 5)
    print(f"Resultado: {resultado}")
    
    print("Llamando suma(10, 20):")
    resultado2 = suma(10, 20)
    print(f"Resultado: {resultado2}")
    print(f"Conteo total de llamadas: {suma.get_count()}")
    print()
    
    print("2. Función con decorador de seguimiento:")
    print("Llamando suma_decorada(7, 3):")
    resultado3 = suma_decorada(7, 3)
    print()
    
    print("🔸 DEMO: Comparación Fibonacci")
    print("=" * 40)
    print("Fibonacci tradicional (lento) vs Generador (eficiente)")
    
    print("\nFibonacci tradicional F(8):")
    fib_tradicional = fibonacci_tradicional(8)
    print(f"Total de llamadas recursivas: {fibonacci_tradicional.get_count()}")
    
    print("\nFibonacci con generador F(8):")
    fib_gen = fibonacci_generator()
    fib_values = []
    for i in range(9):  # 0 a 8
        fib_values.append(next(fib_gen))
    print(f"Valores: {fib_values}")
    print(f"F(8) = {fib_values[8]}")
    print("Solo 9 cálculos (uno por valor, sin recursión)")


def casos_uso_reales():
    """Muestra casos de uso reales y prácticos."""
    print("🎯 CASOS DE USO REALES")
    print("=" * 40)
    
    # Generador para leer archivo línea por línea (simulado)
    def leer_archivo_grande(filename):
        """Simula leer un archivo gigante línea por línea."""
        lines = [f"Línea {i} del archivo {filename}" for i in range(1, 6)]
        for line in lines:
            yield line.strip()
    
    print("📄 Procesando archivo grande:")
    for linea in leer_archivo_grande("datos.txt"):
        print(f"Procesando: {linea}")
    print()
    
    # Generador para números pares infinitos
    def numeros_pares():
        """Genera números pares infinitamente."""
        n = 0
        while True:
            yield n
            n += 2
    
    print("🔢 Primeros 5 números pares:")
    pares = numeros_pares()
    primeros_5_pares = [next(pares) for _ in range(5)]
    print(f"Resultado: {primeros_5_pares}")
    print()
    
    # Pipeline simple con generadores
    def cuadrados(numbers):
        """Generador que eleva al cuadrado."""
        for n in numbers:
            yield n * n
    
    def menores_que(limit):
        """Función que retorna un filtro."""
        def filtro(numbers):
            for n in numbers:
                if n < limit:
                    yield n
        return filtro
    
    print("🔄 Pipeline: números(1-5) → cuadrados → menores_que(20)")
    numeros_base = numbers_generator(1, 5)
    numeros_cuadrados = cuadrados(numeros_base)
    numeros_filtrados = menores_que(20)(numeros_cuadrados)
    
    resultado_pipeline = list(numeros_filtrados)
    print(f"Resultado: {resultado_pipeline}")


# =============================================================================
# MAIN - EJECUTAR DEMOSTRACIONES
# =============================================================================

if __name__ == "__main__":
    print("DECORADORES Y GENERADORES - GUÍA SIMPLE")
    print("=" * 50)
    print()
    
    demostrar_generadores()
    print("\n" + "="*50 + "\n")
    
    demostrar_decoradores()
    print("\n" + "="*50 + "\n")
    
    casos_uso_reales()
    
    print("\n" + "="*50)
    print("📚 RESUMEN:")
    print("• Los GENERADORES producen valores bajo demanda (lazy)")
    print("• Los DECORADORES añaden funcionalidad a funciones")
    print("• Ambos son herramientas de programación funcional")
    print("• Ayudan a escribir código más eficiente y modular")
    print("="*50)
