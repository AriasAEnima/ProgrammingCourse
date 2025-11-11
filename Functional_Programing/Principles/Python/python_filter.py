
l = [2,3,4,5,6]
words = ["casa","patio","kdk","colegio"]
# f => devuelve un booleano 


def has_vowel(word):
    return ('a' in word 
            or 'a' in word 
            or 'e' in word 
            or'i' in word
            or'o' in word 
            or 'u' in word )


print(list(filter(lambda x: x%1==0,l)))

print(list(filter(lambda x: "g" in x,words)))

print(list(filter(has_vowel,words)))

print(list(filter(lambda x: not has_vowel(x),words)))