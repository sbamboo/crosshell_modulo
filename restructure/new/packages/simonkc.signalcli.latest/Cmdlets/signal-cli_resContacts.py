import os

contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))

if os.path.exists(contacts): os.remove(contacts)

csSession.cslib.datafiles._fileHandler("json","set",contacts,{})