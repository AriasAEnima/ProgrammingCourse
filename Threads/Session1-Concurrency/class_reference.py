

class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age 
    
    def saludo_ingles(self):
        print(f"My name is: {self.name} , I am {self.age} years old")


    def __str__(self):
        return f"Mi nombre es: {self.name} y mi edad es: {self.age}"


u = User("Eduardo",29)
print(u)
print(u.saludo_ingles())

def high_order_function(f,n):
    for _ in range(0,n):
        f()

high_order_function(u.saludo_ingles, 10)

juan = User("Juan", 22)

def hello_world():
    print("Hello world")

high_order_function(juan.saludo_ingles,5)

high_order_function(hello_world, 2)