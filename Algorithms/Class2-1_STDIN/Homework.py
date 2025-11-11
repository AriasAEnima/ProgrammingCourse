import fileinput

"""
Create a function that writes the numbers 
in snake form 
1 2  3  4
8 7  6  5
9 10 11 12
"""
def snake_matrix(line):
    return line

def main():
    for line in fileinput.input():
        print(snake_matrix(line))

main()