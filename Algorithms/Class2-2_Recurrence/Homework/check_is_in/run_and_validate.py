# python validate.py < input.txt > output.txt
import Homework_is_in_recursive

def run(input):
    input = str(open('input.txt', "r").read()).split("\n")
    with open('output.txt', 'w') as file:
        # Check this !! 
        for i in range(0, len(input) - 1, 2):
            line_1 = input[i]
            line_2 = input[i+1]
            file.write(f'{Homework_is_in_recursive.init_check_is_in_recursive(line_1, line_2)}\n')

def validate(expect, output):
    expect = str(open(expect, "r").read())
    out = str(open(output, "r").read())
    if expect == out:
        print("OK :), all cases adove are ok !")
    else:
        print("BAD :( , check jumplines also")
        
run("input.txt")
validate("expect.txt","output.txt")