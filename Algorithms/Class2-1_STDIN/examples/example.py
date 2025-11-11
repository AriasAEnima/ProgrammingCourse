import fileinput # Importar librerias

for line in fileinput.input():
    value = len(line.split(","))
    print(value)

