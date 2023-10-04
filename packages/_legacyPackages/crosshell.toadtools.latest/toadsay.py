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
    import threading
    import time
    def timed_toad_msg():
        global timed,argv,toad
        sargv = ' '.join(argv)
        toad.setOnetime(f"{sargv}")
        toad.setPersMsg(f"{sargv}")
        time.sleep(int(timed))
        toad.resPersMsg()
        sInput.liveSetBToolbarMsg(toad.getToadMsg())
    toad_thread = threading.Thread(target=timed_toad_msg)
    toad_thread.start()
# no-timed
else:
    toad.setOnetime(f"{sargv}")