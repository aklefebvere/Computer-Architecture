import sys
# print(sys.argv)
with open(sys.argv[1]) as f:
    for line in f:
        line = line.split("#")
        number = line[0].strip()
        
        if number != '':
            binary = int(number, 2) # convert to int with the base of 2 since we are passing in a b value