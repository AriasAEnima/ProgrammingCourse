# Ivert the list in recursive method
# you can use + or  [:]
# you can't use new functions, 
# hint use also :  pop()
# python <nombredelarchivo>.py < input.txt > output.txt

def reverse_recursive(list,lista_inv_accum):
    if not list:
        return lista_inv_accum
    else: 
        return []

def init_reverse_recursive(line):
    l = line.strip().split(",")
    ans = reverse_recursive(l, list())
    print("ans" ,ans)
    return ','.join(ans)

