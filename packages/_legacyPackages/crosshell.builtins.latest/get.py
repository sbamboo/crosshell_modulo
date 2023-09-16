try:
    key = argv[0]
    val = csSession.data["cvm"].getvar(key)
    if val != None and val != "": print(val)
except:
    pass