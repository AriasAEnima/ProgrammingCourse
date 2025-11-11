
def apply(l,f,g):
    return g(f(l))

# Funcion pura
def multiply_by_2(a):
    return a * 2

# funcion pura
def product(l):
    ans = 1
    print("Product print l: " ,l)

    for e in l:
        ans = ans * e
    print("Product print: " + str(ans))
    return ans
l = [2,3,4]

print(apply(l, sum, multiply_by_2))

print(product(l))

print(apply(l, product, multiply_by_2))
print(apply(l, multiply_by_2, product))

apply(l,lambda x : len(x), lambda y: print("Mi longitud es:", y) )

