toad = csSession.registry["toadInstance"]
sInput = csSession.registry["sInputInstance"]

timed = False
if "-t" in argv:
    tindex = argv.index("-t")
    try:
        timed = argv[tindex+1]
        argv.pop(tindex)
    except: pass
    argv.pop(tindex)

# timed
if timed != False:
    toad.timedMsgNu(' '.join(argv),float(timed))
# no-timed
else:
    toad.setOnetime(f"{sargv}")

toad.updNoSIToad()