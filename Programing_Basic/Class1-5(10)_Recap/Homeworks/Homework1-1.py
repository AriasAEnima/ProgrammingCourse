import fileinput
import Homework

def main():
    double = [True, True, True, True, True,True,True]  
    single = [True, True, True, True, True,True]
    no_spicy = []   # create case
    no_vegetables = [] #create case 

    double_price = Homework.price_hamburger(*double) # Why I have to use * ?
    print(double_price)
    # print cases

main()