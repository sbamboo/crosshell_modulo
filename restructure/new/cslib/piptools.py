import os

# Python
def getExecutingPython() -> str:
    '''CSlib: Returns the path to the python-executable used to start crosshell'''
    return sys.executable

def _check_pip(pipOvw=None) -> bool:
    '''CSlib_INTERNAL: Checks if PIP is present'''
    if pipOvw != None and os.path.exists(pipOvw): pipPath = pipOvw
    else: pipPath = getExecutingPython()
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call([pipPath, "-m", "pip", "--version"], stdout=devnull, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False
    return True

def intpip(pip_args=str,pipOvw=None):
    '''CSlib: Function to use pip from inside python, this function should also install pip if needed (Experimental)
    Returns: bool representing success or not'''
    if pipOvw != None and os.path.exists(pipOvw): pipPath = pipOvw
    else: pipPath = getExecutingPython()
    if not _check_pip(pipOvw):
        print("PIP not found. Installing pip...")
        get_pip_script = "https://bootstrap.pypa.io/get-pip.py"
        try:
            subprocess.check_call([pipPath, "-m", "ensurepip"])
        except subprocess.CalledProcessError:
            print("Failed to install pip using ensurepip. Aborting.")
            return False
        try:
            subprocess.check_call([pipPath, "-m", "pip", "install", "--upgrade", "pip"])
        except subprocess.CalledProcessError:
            print("Failed to upgrade pip. Aborting.")
            return False
        try:
            subprocess.check_call([pipPath, "-m", "pip", "install", get_pip_script])
        except subprocess.CalledProcessError:
            print("Failed to install pip using get-pip.py. Aborting.")
            return False
        print("PIP installed successfully.")
    try:
        subprocess.check_call([pipPath, "-m", "pip"] + pip_args.split())
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to execute pip command: {pip_args}")
        return False

# Safe import function
def autopipImport(moduleName=str,pipName=None,addPipArgsStr=None,cusPip=None,attr=None,relaunch=False,relaunchCmds=None):
    '''CSlib: Tries to import the module, if failed installes using intpip and tries again.'''
    try:
        imported_module = importlib.import_module(moduleName)
    except:
        if pipName != None:
            command = f"install {pipName}"
        else:
            command = f"install {moduleName}"
        if addPipArgsStr != None:
            if not addPipArgsStr.startswith(" "):
                addPipArgsStr = " " + addPipArgsStr
            command += addPipArgsStr
        if cusPip != None:
            #os.system(f"{cusPip} {command}")
            intpip(command,pipOvw=cusPip)
        else:
            intpip(command)
        if relaunch == True and relaunchCmds != None and "--noPipReload" not in relaunchCmds:
            relaunchCmds.append("--noPipReload")
            if "python" not in relaunchCmds[0] and isPythonRuntime(relaunchCmds[0]) == False:
                relaunchCmds = [getExecutingPython(), *relaunchCmds]
            print("Relaunching to attempt reload of path...")
            print(f"With args:\n    {relaunchCmds}")
            subprocess.run([*relaunchCmds])
        else:
            imported_module = importlib.import_module(moduleName)
    if attr != None:
        return getattr(imported_module, attr)
    else:
        return imported_module

# Function to load a module from path
def fromPath(path):
    '''CSlib: Import a module from a path. (Returns <module>)'''
    path = path.replace("/",os.sep).replace("\\",os.sep)
    spec = importlib.util.spec_from_file_location("module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def fromPathAA(path):
    '''CSlib: Import a module from a path, to be used as: globals().update(fromPathAA(<path>)) (Returns <module>.__dict__)'''
    path = path.replace("/",os.sep).replace("\\",os.sep)
    spec = importlib.util.spec_from_file_location("module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__