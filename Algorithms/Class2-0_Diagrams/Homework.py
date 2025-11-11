# First Implement cast binary string to boolean values
# The function must cast binary list to boolean list
# [ "0", "0", "1" ] -> [  False, False, True]
# expected_size greater than binary_list size put extra(s) False on LEFT side
# expected_size must be (always will be) >= len(boolean_list)
# [ "1", "1"] , 3-> [False, True, True]
def binary_to_boolean(binary_list, expected_size):
    pass

# Calculate the maximum posible number of the string list rep. 
# (How many digits can have the binary number)
# The result must be the size of the longest list + 1
# ["1","1"], ["1"] -> 3 / ["1"], ["1","0","1"] -> 4
def define_fixed_size(binary_list_a, binary_list_b):
    pass

# Calculate the sum of A , B and C as Boolean , the result must be two boolean
# Fist the result , next the carry
# Avoid use if or use numbers, just use boolean operators as AND , OR , = , != etc ..
# Hint , first calculate the digit result ((A  _  B) _ C),  
# maybe create trundly tables can help ! 
# to calculate the carry think in permutation operations (A _ B ) (A _ C ) (B _ C)
# True, True , True -> [True, True]
# True , False , True -> [False, True]
def basic_sum(A,B,carry):
    return [True, True]

# Covert a string to list of strings of size 1
# Remember that you can iterate a String as list
# "10101" -> ["1","0","1","0","1"]
# Use append ...
def split_custom(number_string):
    pass

# Covert a list of string to unique string 
# Remember that you can iterate a String as list
#  ["1","0","1","0","1"] -> "1010101"
# use concat ... 
def zip_custom(list_string):
    pass

# Calculate the sum of two binary numbers (strings) (add new digit by default)
# "101" , "1" -> "0110"
# "001" , "0" -> "0001"
# "111" , "111" -> "1110"
def sum_two_numbers(binary_number_a,binary_number_b):
    # use split ,  zip ... etc .. etc ...
    pass