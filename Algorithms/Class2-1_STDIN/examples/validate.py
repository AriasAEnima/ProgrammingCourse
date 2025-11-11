def validate(expect, output):
    expect = open(expect, "r")  
    out = open(output, "r")
    if str(expect.read()) == str(out.read()):
        print("OK :)")
    else:
        print("BAD :(")

validate("expect.txt","output.txt")