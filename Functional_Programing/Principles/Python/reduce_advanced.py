from functools import reduce

users = [{"name":"Eduardo",
         "age": 29},
        {"name":"Juan",
         "age": 20},
         {"name":"Yeferson",
         "age": 27},
         {"name":"Mauricio",
         "age": 30}]

print(reduce(lambda accum, y : str(f"{accum} y {y}"),users))
print("======")
# Eduardo-Juan <= ? String
print(reduce(lambda accum, y : accum+"-"+y["name"],users[1:],users[0]["name"]))
print(reduce(lambda accum, y : accum+"-"+y["name"],users,""))
print(reduce(lambda accum, y : accum+"-"+y["name"],users,"")[1:])
# Edad1 + Edad2 ... = ?
print("======")
# accum es int y Y es un objeto
print(reduce(lambda accum, y : accum+ y["age"],users,0))
print(reduce(lambda accum, y :  accum+ y["age"],users[1:],users[0]["age"]))

# Edad1 * Edad 2 ... = ?
print("======")
# accum es int y Y un objeto
print(reduce(lambda accum, y : accum * y["age"],users,1))

print("======")
# accum es dupla y Y un objeto
def concat_and_sum(accum,y):
    return (accum[0] + y["name"],accum[1] + y["age"])

print(reduce(concat_and_sum,users, ("",0)))

print("======")
# accum es un diccionario y Y tambien
# pero son totalmente distintos.
#     print(f" accum {accum} new element {new_elemt}") <= es tu amigo
def concat_and_sum(accum,y):
    # Accum es una estrucutra muy diferente a Y 
    #acumm = {"edades":0, "nombres":""}
    # y = {"name":"Eduardo", "age": 29}
    return {"edades": y["age"]+accum["edades"] , "nombres": y["name"]+accum["nombres"]}

print(reduce(concat_and_sum,users, {"edades":0, "nombres":""}))

print("======")

# hay alguien mayor a 30 ?
def is_older_than_30(accum,y):
    print(f" accum {accum} new element {y}")
    return accum or (y["age"]>30)

print(reduce(is_older_than_30 , users,False))

print("======")

# x op y 
# [-2,-3]

print(reduce(lambda accum,y: max(accum, y["age"]) , users,users[0]["age"]))

print("======")
# {palabras_con_a: [ ], palbras_con_b: []}

l = ["casa", "sol","bolo"]

def agrupar(accum,y):
    # accum = {palabras_con_a: [ ], palbras_con_b: []}
    print(f" accum {accum} new element {y}")
    if "a" in y:
        return {"palabras_con_a": [y]+ accum["palabras_con_a"] ,
                 "palabras_con_b": accum["palabras_con_b"]  }
    elif "b" in y:
        return {"palabras_con_a":  accum["palabras_con_a"] ,
                 "palabras_con_b": [y]+ accum["palabras_con_b"]  }
    else:
        return accum

print(reduce(agrupar,l,{"palabras_con_a": [], "palabras_con_b": []}))

# X operacion Y = X  ;  Y es el valor indepontente
# X + Y = X    Y ? 0
# X * Y = X    Y ? 1
# X - Y = X    Y ? 0
# X / Y = X    Y ? 1
# X ** Y = X    Y ? 1
# [X] + [Y]  = X  Y ?  []
# "X" + "Y" = "X" Y ? ""
#  X or Y  = X     Y ? False.   X or False 
#  X and Y = X     Y ? True

# Reduccion
# todos son or
# ....... X or True or Y or Z ... or K .....  ?  = True
# Todos son and
# ...... S and False and Q and P and Z  ... ?  = False
# a es mas costoso que b 
# if a or b or c .... d true: 
#.   costosa




