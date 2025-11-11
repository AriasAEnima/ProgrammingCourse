

def addElement(list, new_element):
    list.append(new_element)

def addElement2(list, new_element):
    # new_element = copy of e
    ans = []

    for e in list:
        ans.append(e) # create a copy of list

    ans.append(new_element)
    return ans

l = [2,3,4,5,6]
e = {"name": "Eduardo",
     "lastname": "Arias"}
#print(addElement(l,e))
copy_of_l_with_e = addElement2(l,e)
print(l)
print(copy_of_l_with_e)
e["lastname"] = "Barrera"
print(copy_of_l_with_e)
print(l)