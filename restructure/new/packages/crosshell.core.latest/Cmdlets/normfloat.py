nargvs = []
for arg in args.argv:
    if str(arg).startswith("."):
        nargvs.append( "0"+str(arg) )
    elif str(arg).endswith("."):
        nargvs.append( str(arg)+"0" )
    else:
        nargvs.append( arg )

if len(nargvs) > 1:
    print(str(nargvs))
else:
    if len(nargvs) > 0:
        print(nargvs[0])