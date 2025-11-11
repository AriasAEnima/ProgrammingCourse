import fileinput

"""
Fix the code !!

We know that the ingredients of Hamburger are:

meat, chicken, cheese, lechuce, tomatoes, onion, pickle+

if we have >=1 vegetables the price increase 1  (expect pickles) 

if we have meat increase 2 , or if we have chicke increase 2
but if we have both increase only 3

Pickles increase 1 

All hamburgers have cheese and bread and the price is included 
"""

def price_hamburger(meat, chicken, cheese, lechuce, tomatoes, onion, pickles):
    price = 0
    if (lechuce == True and tomatoes == True and onion == True):
        price += 1   
    if (pickles == True):
        price +=1

    if (meat == True and chicken == True):
        price +=3
    elif (meat == True and chicken == False):
        price +=2
    elif (meat == False and chicken == False):
        price +=2

    return price

def execute_case():   
    print(price_hamburger(True, True, True, False, False, True, False))
