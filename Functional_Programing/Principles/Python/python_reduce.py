
from functools import reduce

def my_sum(l,accum):
    if len(l)==0:
        return accum
    else:
        return my_sum(l[1:],accum+l[0])
    
l = [1,2,3,4,5,6]
print(my_sum(l,0))


print(reduce(lambda x, y: x*y, [2,4,5]))

info = ["Eduardo","Arias","321252888"]


print(reduce(lambda x, y: x+"-"+y, info))

print(list(filter(lambda x: x%2==0, l)))

# l = [1,2,3,4,5,6]
def concatenate_odd(accum,new_elemt):
    print(f" accum {accum} new element {new_elemt}")

    if new_elemt % 2 ==0:
        return accum + [new_elemt]
    else:
        return accum


print(reduce(concatenate_odd,l,[]))

#print(list(filter(lambda x: "g" in x,words)))
# info = ["Eduardo","Arias","321252888"]


def add_contains_a(accum,new_elemt):
    print(f" accum {accum} new element {new_elemt}")

    if 'a' in new_elemt:
        return accum + [new_elemt]
    else:
        return accum
    
print(reduce(add_contains_a,info,[]))

# map words to len of each word
# ["casa","sol","tu"] => [4,3,2]

words = ["casa","sol","tu"]
def add_len(accum,new_elemnt):
    print(f" accum {accum} new element {new_elemnt}")
    return accum + [len(new_elemnt)]

print(reduce(add_len,words,[]))
