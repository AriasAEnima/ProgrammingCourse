

def map_dirty(l, f):
    ans = []
    for e in l:
        ans.append(f(e))
    return ans

def map_less_dirty(l,f,acc):
    if len(l) == 0:
        return acc
    else:
        acc = acc + [f(l[0])]
        return map_less_dirty(l[1:],f,acc)

l = [2,3,4,5,6,7]

print(map_dirty(l,lambda x: x*2))

print(map_less_dirty(l,lambda x: x*2,[]))