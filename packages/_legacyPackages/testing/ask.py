silent = False
if "--s" in argv:
    silent = True
    i = argv.index("--s")
    argv.pop(i)
elif "/s" in argv:
    silent = True
    i = argv.index("/s")
    argv.pop(i)

inp = input(' '.join(argv))
csSession.data["cvm"].chnvar("ans",inp)
if silent != True: print(inp)