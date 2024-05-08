sargv = args.sargv
sargv = sargv.replace("u+","")
sargv = sargv.replace("U+","")

if len(sargv) == 6:
    print("{u."+str(hex(int(sargv))[2:])+"}")
elif len(sargv) == 9 or len(sargv) == 8:
    print(sargv)
elif len(sargv) == 1:
    sargv = f"{ord(sargv):04X}"
    print("{u."+sargv+"}")
else:
    print("{u."+sargv+"}")