

l = ["as","b","cd","d"]
c = [1,2,3,4,5,6]
d = "JUAN"
dir = {"name": "Eduardo",
       "lastname": "Arias"}

print(list(map(lambda x: x*2,l)))
print(list(map(lambda x: len(x),l)))
print(list(map(lambda x: x*2,c)))
print(list(map(lambda x: x*2,d)))
print(list(map(print,dir)))

print(list(map(lambda key: dir[key],dir)))

print(list(map(lambda key: (key.upper(),dir[key].lower()),dir)))