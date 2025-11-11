"""
*args vs **kwargs - Diferencias y Ejemplos Claros
=================================================

Este archivo explica de forma simple las diferencias entre *args y **kwargs
con ejemplos paso a paso.
"""

# =============================================================================
# ¿QUÉ SON *args Y **kwargs?
# =============================================================================

def explicacion_basica():
    """Explicación conceptual de args y kwargs."""
    print("📚 CONCEPTOS BÁSICOS:")
    print("=" * 50)
    print("• *args  = argumentos posicionales variables (tupla)")
    print("• **kwargs = argumentos con nombre variables (diccionario)")
    print("• Se usan para funciones que aceptan cantidad variable de parámetros")
    print()


# =============================================================================
# EJEMPLOS PASO A PASO
# =============================================================================
# (a,b,c)
# {a: 1 , b: 2 , c:3}
def funcion_con_args(*args):
    """Función que acepta cualquier cantidad de argumentos posicionales."""
    print(f"Tipo de args: {type(args)}")
    print(f"Contenido de args: {args}")
    print(f"Cantidad de argumentos: {len(args)}")
    
    print("Argumentos uno por uno:")
    for i, arg in enumerate(args):
        print(f"  Argumento {i}: {arg}")
    print()


def funcion_con_kwargs(**kwargs):
    """Función que acepta cualquier cantidad de argumentos con nombre."""
    print(f"Tipo de kwargs: {type(kwargs)}")
    print(f"Contenido de kwargs: {kwargs}")
    print(f"Cantidad de argumentos: {len(kwargs)}")
    
    print("Argumentos con nombre uno por uno:")
    for clave, valor in kwargs.items():
        print(f"  {clave} = {valor}")
    print()


def funcion_completa(parametro_normal, *args, **kwargs):
    """Función que combina parámetros normales, *args y **kwargs."""
    print(f"Parámetro normal: {parametro_normal}")
    print(f"Args adicionales: {args}")
    print(f"Kwargs adicionales: {kwargs}")
    print()

"""
a= ... 
b = cc
"""
def funcion_con_todo(requerido, opcional="default", *args, **kwargs):
    """Función que muestra el orden correcto de todos los tipos de parámetros."""
    print(f"1. Parámetro requerido: {requerido}")
    print(f"2. Parámetro opcional: {opcional}")
    print(f"3. Args variables: {args}")
    print(f"4. Kwargs variables: {kwargs}")
    print()


# =============================================================================
# CASOS DE USO PRÁCTICOS
# =============================================================================

def suma_flexible(*numeros):
    """Suma cualquier cantidad de números."""
    if not numeros:
        return 0
    
    total = sum(numeros)
    print(f"Sumando: {numeros}")
    print(f"Resultado: {total}")
    return total


def saludar(mensaje, *nombres, **opciones):
    """Saluda a múltiples personas con opciones personalizables."""
    estilo = opciones.get('estilo', 'formal')
    idioma = opciones.get('idioma', 'español')
    mayuscula = opciones.get('mayuscula', False)
    
    print(f"Mensaje base: {mensaje}")
    print(f"Estilo: {estilo}, Idioma: {idioma}")
    
    for nombre in nombres:
        saludo_final = f"{mensaje} {nombre}"
        if mayuscula:
            saludo_final = saludo_final.upper()
        print(f"  → {saludo_final}")
    print()


def crear_perfil(**datos_usuario):
    """Crea un perfil de usuario con cualquier cantidad de campos."""
    print("👤 CREANDO PERFIL DE USUARIO:")
    
    # Campos requeridos
    campos_requeridos = ['nombre', 'email']
    for campo in campos_requeridos:
        if campo not in datos_usuario:
            print(f"❌ Error: Campo '{campo}' es requerido")
            return None
    
    # Mostrar todos los datos
    for campo, valor in datos_usuario.items():
        print(f"  {campo.capitalize()}: {valor}")
    
    print("✅ Perfil creado exitosamente")
    return datos_usuario


# =============================================================================
# EJEMPLOS CON DECORADORES (DEL ARCHIVO ANTERIOR)
# =============================================================================

def decorador_flexible(*dec_args, **dec_kwargs):
    """Decorador que puede recibir argumentos opcionales."""
    print(f"🎭 Creando decorador con args: {dec_args}, kwargs: {dec_kwargs}")
    
    def decorador_real(func):
        def wrapper(*func_args, **func_kwargs):
            print(f"🔧 Decorando función: {func.__name__}")
            print(f"   Args del decorador: {dec_args}")
            print(f"   Kwargs del decorador: {dec_kwargs}")
            print(f"   Args de la función: {func_args}")
            print(f"   Kwargs de la función: {func_kwargs}")
            
            resultado = func(*func_args, **func_kwargs)
            return resultado
        return wrapper
    return decorador_real

# debug se recibe en dec_args
# y nivel y activo se recibe en dec_kwargs
# llamo a decorador_flexible y lo que me devuelva f aplico los argumentos de la funcion decorador
# decorador_real permite ejecutar operacion_matematica + arguementos de decorador flexibles
@decorador_flexible("debug", nivel=1, activo=True)
def operacion_matematica(a, b, operacion="suma"): # no esta escrito ningun parametro * o **
    """Función de ejemplo para mostrar decorador flexible."""
    if operacion == "suma":
        return a + b
    elif operacion == "multiplicacion":
        return a * b
    return 0


# =============================================================================
# DEMOSTRACIONES INTERACTIVAS
# =============================================================================

def demo_args():
    """Demuestra el uso de *args."""
    print("🔹 DEMO: *args (argumentos posicionales variables)")
    print("=" * 60)
    
    print("1. Llamando funcion_con_args(1, 2, 3):")
    funcion_con_args(1, 2, 3)
    
    print("2. Llamando funcion_con_args('a', 'b', 'c', 'd'):")
    funcion_con_args('a', 'b', 'c', 'd')
    
    print("3. Llamando funcion_con_args() [sin argumentos]:")
    funcion_con_args()
    
    print("4. Ejemplo práctico - suma flexible:")
    suma_flexible(1, 2, 3, 4, 5)
    suma_flexible(10, 20)
    suma_flexible()


def demo_kwargs():
    """Demuestra el uso de **kwargs."""
    print("🔸 DEMO: **kwargs (argumentos con nombre variables)")
    print("=" * 60)
    
    print("1. Llamando funcion_con_kwargs(nombre='Ana', edad=25):")
    funcion_con_kwargs(nombre='Ana', edad=25)
    
    print("2. Llamando funcion_con_kwargs(color='azul', tamaño='grande', precio=100):")
    funcion_con_kwargs(color='azul', tamaño='grande', precio=100)
    
    print("3. Ejemplo práctico - crear perfil:")
    crear_perfil(
        nombre="Eduardo",
        email="eduardo@example.com",
        edad=30,
        ciudad="São Paulo",
        profesion="Desarrollador"
    )


def demo_combinados():
    """Demuestra el uso combinado de args y kwargs."""
    print("🔄 DEMO: *args + **kwargs combinados")
    print("=" * 60)
    
    print("1. Función completa con parámetros mixtos:")
    funcion_completa("valor_fijo", 1, 2, 3, nombre="Ana", activo=True)
    
    print("2. Función con todo tipo de parámetros:")
    funcion_con_todo("requerido", "opcional_custom", 10, 20, 30, debug=True, nivel=5)
    
    print("3. Ejemplo práctico - saludar flexible:")
    saludar(
        "Hola",
        "Ana", "Carlos", "María",
        estilo="casual",
        idioma="español",
        mayuscula=True
    )
    
    print("4. Decorador flexible:")
    resultado = operacion_matematica(5, 3, operacion="multiplicacion")
    print(f"Resultado de la operación: {resultado}")


def demo_diferencias():
    """Muestra las diferencias clave entre args y kwargs."""
    print("⚖️  DIFERENCIAS CLAVE")
    print("=" * 60)
    
    # Crear listas para mostrar diferencias
    datos_args = (1, 2, 3, "texto", True)
    datos_kwargs = {"nombre": "Ana", "edad": 25, "activo": True}
    
    print("📋 COMPARACIÓN DIRECTA:")
    print(f"  *args es una TUPLA:      {type(datos_args)} = {datos_args}")
    print(f"  **kwargs es DICCIONARIO: {type(datos_kwargs)} = {datos_kwargs}")
    print()
    
    print("🔍 ACCESO A DATOS:")
    print("  *args se accede por índice:")
    print(f"    args[0] = {datos_args[0]}")
    print(f"    args[1] = {datos_args[1]}")
    
    print("  **kwargs se accede por clave:")
    print(f"    kwargs['nombre'] = {datos_kwargs['nombre']}")
    print(f"    kwargs['edad'] = {datos_kwargs['edad']}")
    print()
    
    print("📞 FORMA DE LLAMAR:")
    print("  *args:   funcion(1, 2, 3, 'texto')")
    print("  **kwargs: funcion(nombre='Ana', edad=25)")
    print("  Ambos:    funcion(1, 2, nombre='Ana', edad=25)")
    print()


# =============================================================================
# MAIN - EJECUTAR TODAS LAS DEMOSTRACIONES
# =============================================================================

if __name__ == "__main__":
    print("*ARGS vs **KWARGS - GUÍA COMPLETA")
    print("=" * 70)
    print()
    
    explicacion_basica()
    
    demo_args()
    print("\n" + "="*70 + "\n")
    
    demo_kwargs()
    print("\n" + "="*70 + "\n")
    
    demo_combinados()
    print("\n" + "="*70 + "\n")
    
    demo_diferencias()
    
    print("="*70)
    print("🎯 RESUMEN FINAL:")
    print("• *args  = lista/tupla de valores → func(1, 2, 3)")
    print("• **kwargs = diccionario clave=valor → func(name='Ana', age=25)")
    print("• Orden: func(normal, *args, **kwargs)")
    print("• Útiles para funciones flexibles y decoradores")
    print("="*70)
