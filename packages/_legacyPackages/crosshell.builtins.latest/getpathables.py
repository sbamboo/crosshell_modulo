items = csSession.registry["cmdlets"]
keys =  csSession.registry["cmdlets"].keys()

title = "{f.magenta}Loaded cmdlets:"

aliases = {}
for key in keys:
    for alias in items[key]["aliases"]:
        aliases[alias] = key

if sargv.strip("") != "":
    q_keys = []
    for arg in argv:
        arg = arg.strip()
        if arg in list(keys):
            q_keys.append(arg)
        elif arg in list(aliases.keys()):
            q_keys.append(aliases[arg])
    if q_keys == []:
        print(f"Query invalid! ('{sargv}')")
        exit()
    else:
        keys = q_keys

title = "{f.magenta}Loaded cmdlets (query):"

print(title)
for key in keys:
    value = items[key]
    print("{f.yellow}"+f'\n  {key}:'+"{r}")
    print("{f.darkgray}     desc:{f.green}"+f' "{value["desc"]}"')
    print("{f.darkgray}     aliases{f.green}"+f' {value["aliases"]}')
    print("{f.darkgray}     args{f.green}"+f' "{value["args"]}"')
    print("{f.darkgray}     bcp{f.green}"+f' {value["blockCommonParameters"]}')
    print("{f.darkgray}     encoding{f.green}"+f' {value["encoding"]}')
    print("{f.darkgray}     fending{f.green}"+f' {value["fending"]}')
    print("{f.darkgray}     options:")
    print("{f.darkgray}        argparseHelp{f.green}"+f' {value["options"]["argparseHelp"]}')
    print("{f.darkgray}        synopsisDesc{f.green}"+f' {value["options"]["synopsisDesc"]}')
    print("{f.darkgray}        restrictionMode{f.green}"+f' {value["options"]["restrictionMode"]}')
    print("{f.darkgray}        readerReturnVars{f.green}"+f' {value["options"]["readerReturnVars"]}')
    print("{f.darkgray}     path{f.green}"+f' {value["path"]}')
    print("{f.darkgray}     extras{f.green}"+f' {value["extras"]}')
print("{r}")