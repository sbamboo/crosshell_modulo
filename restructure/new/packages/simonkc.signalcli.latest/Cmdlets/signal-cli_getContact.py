import os

contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))

if not os.path.exists(contacts): current = {}
else:
    current = csSession.cslib.datafiles._fileHandler("json","get",contacts)

res = current.get(args.pargv[0].strip('"'))

if res == None: res = ""

print(res)