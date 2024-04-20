import os, json

contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))

if not os.path.exists(contacts): current = {}
else:
    current = csSession.cslib.datafiles._fileHandler("json","get",contacts)

print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("    Signal-Cli Cmdlet Contacts:")
print("- - - - - - - - - - - - - - - - - -")
for k,v in current.items():
    print(f"  {k}  =  {v}")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")