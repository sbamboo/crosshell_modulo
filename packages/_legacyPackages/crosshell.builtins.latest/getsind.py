try:
    ind = argv[0]
    val = argv[1:]
    
    if "\n" in val:
        val = val.split("\n")

    try:
        val = val[int(ind)]
    except:
        val = val[ind]
    if val != None and val != "": print(val)
except:
    pass