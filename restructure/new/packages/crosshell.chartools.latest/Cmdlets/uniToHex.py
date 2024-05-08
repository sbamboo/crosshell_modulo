sargv = args.sargv
sargv = sargv.replace("u+","")
sargv = sargv.replace("U+","")

if len(sargv) == 6:
    print(str(hex(int(sargv))[2:]))
elif len(sargv) == 9 or len(sargv) == 8:
    sargv = sargv.lstrip("{u.").rstrip("}")
    print(sargv)
elif len(sargv) == 1:
    print(f"{ord(sargv):04X}")
else:
    print(sargv)