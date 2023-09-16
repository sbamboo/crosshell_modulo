try:
    key = argv[0]
    value = (' '.join(argv[1:])).strip(" ")
    csSession.data["cvm"].chnvar(key,value)
except:
    pass