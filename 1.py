f = open("t.txt","+r").readlines()
for st in f:
    print(list(map(int,st)))