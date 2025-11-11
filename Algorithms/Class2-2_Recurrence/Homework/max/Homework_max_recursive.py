
# Find the max...
# you can use max(n1, n2)
def max_recursive(l, maxinum):
    pass

def init_max_recursive(line):
    l = line.strip().split(",")
    # Why l[0] what if you put 0 ? 
    ans = max_recursive(l,l[0])
    print("ans" ,ans)
    return ans

