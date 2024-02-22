try:
    ind = argv[-1]
    argv.pop(-1)
    sargv = sargv.replace(f" {ind}","")

    if "\n" in sargv:
        argv = sargv.split("\n")

    val = argv
    print(val)
    try:
        val = val[int(ind)]
    except:
        val = val[ind]
    if val != None and val != "": print(val)
except:
    pass