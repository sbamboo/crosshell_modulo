import os

contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))

if not os.path.exists(contacts): current = {}
else:
    current = csSession.cslib.datafiles._fileHandler("json","get",contacts)

if current.get(args.pargv[0].strip('"')) != None:
    del current[args.pargv[0].strip('"')]

csSession.cslib.datafiles._fileHandler("json","set",contacts,current)