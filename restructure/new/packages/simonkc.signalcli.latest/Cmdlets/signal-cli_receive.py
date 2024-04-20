import os, subprocess

def hContact(string):
    contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))
    if not os.path.exists(contacts): current = {}
    else:
        current = csSession.cslib.datafiles._fileHandler("json","get",contacts)
    if current.get(string) != None: return current[string]
    else: return string

path = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","signal-cli","bin"))

runtime = None

if csSession.exlibs.conUtils.IsWindows() == True:
    runtime = os.path.join(path,"signal-cli.bat")
else:
    runtime = os.path.join(path,"signal-cli")

if runtime == None:
    print("Runtime could't be retrived, please reinstall this package!")
else:
    if not os.path.exists(runtime):
        print("Runtime could't be found, please reinstall this package!")
    else:
        command = [runtime,"-a",hContact(args.pargv[0].strip('"')),"receive"]
        if len(args.argv) > 1:
            command.extend(["--max-messages",args.pargv[1]])
        subprocess.run(command, shell=True)