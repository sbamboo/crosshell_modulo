import os, subprocess

def hContact(string):
    contacts = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","contacts.json"))
    if not os.path.exists(contacts): current = {}
    else:
        current = csSession.cslib.datafiles._fileHandler("json","get",contacts)
    if current.get(string) != None: return current[string]
    else: return string

strToQr = os.path.join(os.path.dirname(CSScriptRoot),"str-to-qr.py")

path = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","signal-cli","bin"))

timeout = 10

if len(args.argv) > 1:
    timeout = args.pargv[1]

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
        try:
            process = subprocess.Popen([runtime,"-a",hContact(args.pargv[0].strip('"')),"jsonRpc"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    
            process.stdin.write(args.pargv[1].strip("'"))
            process.stdin.flush()

            # Read and print output line by line
            for line in process.stdout:
                print(line,end="")

            # Wait for the process to finish
            try:
                process.wait(10)
            except KeyboardInterrupt:
                process.terminate()
        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit status, print the error
            print(e.output)