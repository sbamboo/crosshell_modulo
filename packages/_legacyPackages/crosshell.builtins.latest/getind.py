try:
    key = argv[0]
    ind = argv[1]
    val = csSession.data["cvm"].getvar(key)
    try:
        val = val[int(ind)]
    except:
        val = val[ind]
    if val != None and val != "": print(val)
except:
    pass