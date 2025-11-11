
# encontrar la posicion de la primera ocurrencia de izquierda a derecha de un numero ...
# input [2,4,5,6,7], 5
# output 2
# en caso de que no este imprimir -1
def check_is_in_recursive(l, e):
    if not l:
        pass
    elif l.pop() == e:
        # why two end cases ? 
        pass
    else:
        # Take care about l.pop() changes adove
        pass 

def init_check_is_in_recursive(line_1,line_2):
    l = line_1.strip().split(",")
    l2 = line_2.strip()
    ans = check_is_in_recursive(l, l2)
    print("ans" ,ans)
    return ans

