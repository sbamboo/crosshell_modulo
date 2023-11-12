try:
    if CS_InPipeline == True:
        key = argv[-1]
        value = (' '.join(argv[:-1])).strip(" ")
    else:
        key = argv[0]
        value = (' '.join(argv[1:])).strip(" ")
    cur = csSession.data["cvm"].getvar(key)
    value += cur
    csSession.data["cvm"].chnvar(key,value)
except:
    pass