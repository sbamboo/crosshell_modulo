items = csSession.registry["cmdlets"]
keys =  csSession.registry["cmdlets"].keys()

title = "{f.magenta}Loaded cmdlets:"

try:
    if argv[0].strip() in list(keys):
        keys = [argv[0]]
except: pass

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