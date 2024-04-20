import os, subprocess

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
        subprocess.run([runtime,*args.argv], shell=True)