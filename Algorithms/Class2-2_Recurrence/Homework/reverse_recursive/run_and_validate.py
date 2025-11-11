# python validate.py < input.txt > output.txt
import Homework_invert_recursive

def run(input):
    input = str(open('input.txt', "r").read()).split("\n")
    with open('output.txt', 'w') as file:
        for line in input:
            file.write(f'{Homework_invert_recursive.init_reverse_recursive(line)}\n')

def validate(expect, output):
    expect = str(open(expect, "r").read())
    out = str(open(output, "r").read())
    if expect == out:
        print("OK :), all cases adove are ok !")
    else:
        print("BAD :( , check jumplines also")
        
run("input.txt")
validate("expect.txt","output.txt")