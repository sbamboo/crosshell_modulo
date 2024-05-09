# Shortcuts are <shortcutStr> -> (<keypath>,<filter>,<mode>,<compact>)
# Set filter to None to not change the user defined filter and the same with mode and compact
shortcuts = {
    "#cmdletids": ("LoadedPackageData.cmdlets.data",None,None,None),
    "#cmdlets": ("LoadedPackageData.cmdlets.data","name","values",("","\n"))
}

helpText = "{f.darkmagenta}Additional arguments are:\n{f.darkblue}--v{f.darkgray}: Display values.\n{f.darkblue}--e{f.darkgray}: Display entries.\n{f.darkblue}--l{f.darkgray}: To only get the lenght of the result.\n{f.darkblue}--s{f.darkgray}: For non-formated raw output and ommitted warns/errors.\n{f.darkblue}--c{f.darkgray}: To display a more compact view.\n{f.darkblue}-f {f.blue}<subkeypath>{f.darkgray}: To apply a keypath to each entry. (not keys)\n{f.darkblue}--h{f.darkgray}: Displays this help text.{r}"

mode = None
silent = False
lengthOnly = False
doFilter = False

compact = "\n\n"
compact2 = "\n\n"

if "--v" in args.argv:
    mode = "values"
    args.argv.remove("--v")

if "--e" in args.argv:
    mode = "entries"
    args.argv.remove("--e")

if "--s" in args.argv:
    silent = True
    args.argv.remove("--s")

if "--l" in args.argv:
    lengthOnly = True
    args.argv.remove("--l")

if "--c" in args.argv:
    compact = ""
    compact2 = "\n"
    args.argv.remove("--c")

if "-f" in args.argv:
    ind = args.argv.index("-f")
    if len(args.argv) > ind+1:
        doFilter = args.argv[ind+1]
        args.argv.pop(ind+1)
        args.argv.remove("-f")
    else:
        args.argv.remove("-f")

if "--h" in args.argv:
    csSession.fprint(helpText)
    exit()

if len(args.argv) > 0:
    keypath = args.argv[0]
else:
    if silent == False: csSession.deb.perror("{f.darkred}Wrong amount of arguments given! List takes a keypath to apply to regionals.\n"+helpText)
    exit()

if keypath in shortcuts.keys():
    if len(shortcuts[keypath]) > 1:
        if shortcuts[keypath][1] != None and doFilter == False:
            doFilter = shortcuts[keypath][1]
        if len(shortcuts[keypath]) > 2:
            if shortcuts[keypath][2] != None and mode == None:
                mode = shortcuts[keypath][2]
            if len(shortcuts[keypath]) > 3:
                if shortcuts[keypath][3] != None:
                    compact = shortcuts[keypath][3][0]
                    compact2 = shortcuts[keypath][3][1]
    keypath = shortcuts[keypath][0]

if mode == None: mode = "keys"

if keypath == "*":
    res = csSession.regionalGet()
else:
    res = csSession.cslib.datafiles.getKeyPath( csSession.regionalGet(), keypath )

if res == None and silent == False:
    if mode == "keys":
        csSession.deb.pwarn("{f.darkyellow}No key or empty key at '"+keypath+"'!{r}")
    elif mode == "values":
        csSession.deb.pwarn("{f.darkyellow}No value or empty value at '"+keypath+"'!{r}")
    elif mode == "entries":
        csSession.deb.pwarn("{f.darkyellow}No entries or empty entries at '"+keypath+"'!{r}")
    else:
        csSession.deb.perror("{f.darkred}The path '"+keypath+"' returned empty, invalid mode?{r}")
else:
    if lengthOnly == True:
        if silent == False:
            csSession.fprint("{f.darkgray}Length: "+str(len(res.keys()))+"{r}")
        else:
            print(len(res.keys()))
    else:
        if mode == "keys":
            dat = list(res.keys())
            if silent == False: 
                csSession.fprint("{f.darkgray}Length: "+str(len(dat))+"\n{f.darkmagenta}Keys{f.darkgray}: {f.blue}"+'{f.darkgray}, {f.blue}'.join(dat)+"{r}")
            else:
                print(','.join(dat))

        elif mode == "values":
            if doFilter != False:
                dat = list([str(csSession.cslib.datafiles.getKeyPath(v,doFilter)) if doFilter not in [None,""] else str(v) for v in res.values()])
            else:
                dat = list([str(v) for v in res.values()])

            if silent == False: 
                csSession.fprint("{f.darkgray}Length: "+str(len(dat))+compact2+"{f.darkmagenta}Values{f.darkgray}: {f.blue}"+str('{f.darkgray}, '+compact+'{f.blue}').join(dat)+"{r}")
            else:
                print(','.join(dat))

        elif mode == "entries":
            dat = {}
            if doFilter != False:
                for k_,v_ in res.items():
                    if doFilter not in [None,""]:
                        if silent == False:
                            dat[k_] = csSession.cslib.datafiles.getKeyPath(v_,doFilter)
                        else:
                            csSession.cslib.datafiles.setKeyPath(dat,k_+"."+doFilter, csSession.cslib.datafiles.getKeyPath(v_,doFilter) )
                    else:
                        dat[k_] = v_
            else:
                dat = res
            if silent == False: 
                csSession.fprint("{f.darkgray}Length: "+str(len(dat.keys()))+compact2+"{f.darkmagenta}Entries:\n"+'\n'.join(["{f.darkgreen}"+str(k)+"{f.darkgray}: {f.blue}"+str(v)+compact for k,v in dat.items() ])+"{r}")
            else:
                print(str(dat))

        else:
            csSession.fprint("{f.darkgray}Length: "+str(len(res.keys()))+compact2+"{f.darkyellow}Unknown mode:{f.blue}\n"+str(res))