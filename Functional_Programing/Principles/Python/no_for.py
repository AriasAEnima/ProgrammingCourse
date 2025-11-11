


l = ["A","B","C","D"]

for e in l:
    #print(e)
    pass

print(f"valor e: {e}")

for i in range(0, len(l)):
    #print(l[i])
    pass

print(f"valor i: {i}")


def print_elements(l):
    if len(l)==0:
        return
    else:
        print(l[0])
        print_elements(l[1:])

def add_element(l,e):
    return l[:-1]+[e]

# Imprime el elemento en la posicion idx
def print_elemnt(l,idx):
    if idx == 0:
        print(l[0])
        return l[0]
    else:
        return print_elemnt(l[1:],idx-1)

#print_elements(l)
print(print_elemnt(l,2))

print(add_element(l,4))