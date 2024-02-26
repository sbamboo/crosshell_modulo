import pickle, sys, json, os, argparse, inspect

from cslib.crosshellParsingEngine import tagSubstitionManager, pathTagManager

def normPathSep(path):
    """CSlib: Normalises path sepparators to the current OS."""
    return path.replace("/",os.sep).replace("\\",os.sep)

def normPathSepObj(obj):
    """CSlib: Normalises path sepparators to the current OS in a given object."""
    if type(obj) == dict:
        for k,v in obj.items():
            obj[k] = normPathSepObj(v)
    elif type(obj) == list or type(obj) == tuple:
        for i,v in enumerate(obj):
            obj[i] = normPathSepObj(v)
    elif type(obj) == str:
        obj = normPathSep(obj)
    return obj

def absPathSepObj(obj):
    """CSlib: Absolutes paths in a given object."""
    if type(obj) == dict:
        for k,v in obj.items():
            obj[k] = absPathSepObj(v)
    elif type(obj) == list or type(obj) == tuple:
        for i,v in enumerate(obj):
            obj[i] = absPathSepObj(v)
    elif type(obj) == str:
        obj = os.path.abspath(obj)
    return obj

class UnserializableObjectReference():
    def __init__(self,reference=str):
        self.reference = reference
    def __repr__(self):
        return f'<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}, referencing: {self.reference}>'

class sessionStorage():
    def __init__(self,regionalPrefix=""):
        self.regionalPrefix = regionalPrefix
        self.storage = {
            "tempData": {},
            "userVars": {},
            "regionalScope": {}
        }
    # region: sessionStorage.mainmethods
    def reset(self, key):
        self.storage = {
            "tempData": {},
            "userVars": {},
            "regionalScope": {}
        }
    def __setitem__(self, key, value):
        self.storage[key] = value
    def __getitem__(self, key):
        return self.storage[key]
    def remove(self, key):
        del self.storage[key]
    def update(self, newDict):
        self.storage.update(newDict)
        return self.storage
    # endregion
    
    # region sessionStorage.regionalmethods
    def regionalSet(self, key, value):
        self.storage["regionalScope"][key] = value
    def regionalGet(self, key=None):
        if key == None:
            return self.storage["regionalScope"]
        else:
            return self.storage["regionalScope"][key]
    def regionalRemove(self, key):
        del self.storage["regionalScope"][key]
    def regionalUpdate(self, newDict):
        self.storage["regionalScope"].update(newDict)
        return self.storage["regionalScope"]
    def regionalReset(self):
        self.storage["regionalScope"] = {}
    def regionalExport(self, key=None):
        if key == None:
            toExprt = {}
            for key,value in self.storage["regionalScope"].items():
                toExprt[self.regionalPrefix+key] = value
            return toExprt
        else:
            return {
                self.regionalPrefix+key: self.storage["regionalScope"]
            }
    # endregion

    # region: sessionStorage.tempmethods
    def tempSet(self, key, value):
        self.storage["tempData"][key] = value
    def tempGet(self, key=None):
        if key == None:
            return self.storage["tempData"]
        else:
            return self.storage["tempData"][key]
    def tempRemove(self, key):
        del self.storage["tempData"][key]
    def tempUpdate(self, newDict):
        self.storage["tempData"].update(newDict)
        return self.storage["tempData"]
    def tempReset(self):
        self.storage["tempData"] = {}
    # endregion
    
    # region: sessionStorage.usermethods
    def userVarSet(self, key, value):
        self.storage["userVars"][key] = value
    def userVarGet(self, key=None):
        if key == None:
            return self.storage["userVars"]
        else:
            return self.storage["userVars"][key]
    def userVarRemove(self, key):
        del self.storage["userVars"][key]
    def userVarUpdate(self, newDict):
        self.storage["userVars"].update(newDict)
        return self.storage["userVars"]
    def userVarReset(self):
        self.storage["userVars"] = {}
    # endregion

class crshSession():
    # The identification is used on import to ensure classes are compatible.
    global identification; identification = "f09682eb-5be1-4675-b9a0-68148b48e09c"

    def __init__(self, nonRegisterableTypes=["str","list","tuple","dict","int","float","bool","NoneType"], initOnStart=False, regionalVarPrefix="CS_"):
        self.identification = identification

        self.storage = sessionStorage()
        self.tmpSet = self.storage.tempSet
        self.tmpGet = self.storage.tempGet
        self.tmpRemove = self.storage.tempRemove
        self.tmpUpdate = self.storage.tempUpdate
        self.tmpReset = self.storage.tempReset
        self.userVarSet = self.storage.userVarSet
        self.userVarGet = self.storage.userVarGet
        self.userVarRemove = self.storage.userVarRemove
        self.userVarUpdate = self.storage.userVarUpdate
        self.userVarReset = self.storage.userVarReset
        self.regionalSet = self.storage.regionalSet
        self.regionalGet = self.storage.regionalGet
        self.regionalRemove = self.storage.regionalRemove
        self.regionalUpdate = self.storage.regionalUpdate
        self.regionalReset = self.storage.regionalReset

        self.registry = {}
        self.nonRegisterableTypes = nonRegisterableTypes

        self.regionalPrefix = self.storage.regionalPrefix = regionalVarPrefix

        if initOnStart == True:
            self.init()

    def exprt(self,filename,asJson=False):
        """Exports the current session to a file."""
        if asJson == True:
            with open(filename, 'w') as f:
                f.write( json.dumps(self.__dict__) )
        else:
            with open(filename, 'wb') as f:
                pickle.dump(self,f)

    def imprt(self,filename,asJson=False):
        """Imports a session from a file."""
        if sys.modules.get("main") is None:
            sys.modules["main"] = sys.modules[__name__]
        with open(filename, 'rb') as f:
            if asJson == True:
                loaded_session_dict = json.load(f)
            else:
                loaded_session_dict = pickle.load(f).__dict__
            if None in [loaded_session_dict.get("identification"), self.__dict__.get("identification")]:
                raise Exception("The session file is not compatible with this version of crosshell. (No identification found)")
            if loaded_session_dict["identification"] == self.__dict__["identification"]:
                # Update the attributes of the current session with the loaded session
                self.__dict__.update(loaded_session_dict)
            else:
                raise Exception("The session file is not compatible with this version of crosshell. (Non-matching session.identtification)")

    def register(self, name, object_):
        """Adds an object to the session-registry."""
        if type(object_) in self.nonRegisterableTypes:
            raise TypeError(f"Objects of type {type(object_)} is not registerable, as it's meant for functions/classInstances and methods. For other types use classStorage.")
        elif isinstance(object_, crshSession):
            raise TypeError("A crosshell-session object cannot be registered, to prevent nesting.")
        self.registry[name] = object_

    def unregister(self, name):
        """Unregisters an object from the session-registry."""
        if self.registry.get(name) != None:
            del self.registry[name]
        else:
            raise KeyError(f"No object with the name '{name}' found in the registry.")
    
    def reset_registry(self):
        """Careful! This will remove all registry items!"""
        self.registry = {}

    def getregister(self,name):
        """Returns the object from the registry."""
        if self.registry.get(name) != None:
            return self.registry[name]
        else:
            raise KeyError(f"No object with the name '{name}' found in the registry.")

    def init(self, cliArgs=None, regionalVars=None, argumentDeffinionOvw=None, cmdArgPlaceholders=None):
        """Initiates the session."""

        # Define standard
        _regionalVars = {
            "SessionIdentifier": self.identification,
            "DefaultEncoding": "utf-8",
            "RootPathRetrivalMode": "inspect",

            "CSlibDir": None,
            "BaseDir": "{CSlibDir}/..",
            "CoreDir": "{BaseDir}/core",
            "AssetsDir": "{BaseDir}/assets",
            "PackagesFolder": "{BaseDir}/packages",
            "CS_mPackPath": "{PackagesFolder}",
            "CS_lPackPath": "{PackagesFolder}/_legacyPackages",
            "ReadersFolder": "{CoreDir}/readers",
            "SettingsFile": "{AssetsDir}/settings.json",
            "PersistanceFile": "{AssetsDir}/persistance.json",
            "sInputHistoryFile": "{AssetsDir}/.history",
            "CmdletScopeVarsFile": "{CoreDir}/cmdletScopeVars.json",
            "VersionFile": "{CoreDir}/version.yaml",
            "MsgProfileFile": "{AssetsDir}/profile.msg",
            "PyProfileFile": "{AssetsDir}/profile.py",
            "BuiltInReaders": {
                "PLATFORM_EXECUTABLE": "{ReadersFolder}/platexecs.py"
            },

            "Args": None,
            "Startfile": None,
            "Efile": None,
            "Argparser": None,
            "Pargs": None,
            "StripAnsi": None,
            "PythonPath": sys.executable,
            "PathTags": None
        }

        # Deffine Arguments
        _arguments = [
            [
                ["-sa", "--stripAnsi"],
                {
                    "dest": "stripAnsi",
                    "action": "store_true",
                    "help": "Strips ANSI from output."
                }
            ],
            [
                ["-c", "-cmd"],
                {
                    "dest": "cmd",
                    "help": "Command to execute on start."
                }
            ],
            [
                ["-scr", "-script"],
                {
                    "dest": "script",
                    "help": "Runns a script on start."
                }
            ],
            [
                ["--noverbstart"],
                {
                    "dest": "noverbstart",
                    "action": "store_true",
                    "help": "Suppresses verbose start."
                }
            ],
            [
                ["--noexit"],
                {
                    "dest": "noexit",
                    "action": "store_true",
                    "help": "Keeps crosshell started post cli-command execution."
                }
            ],
            [
                ["--nowelc"],
                {
                    "dest": "nowelc",
                    "action": "store_true",
                    "help": "Suppresses crosshells welcome message."
                }
            ],
            [
                ["--nocls"],
                {
                    "dest": "nocls",
                    "action": "store_true",
                    "help": "Suppresses startup-clear. (if such is enabled in settings)"
                }
            ]
        ]

        _cmdArgPlaceholders = {
            "§": " "
        }

        if argumentDeffinionOvw != None: _arguments = argumentDeffinionOvw
        if cmdArgPlaceholders != None: _cmdArgPlaceholders.update(cmdArgPlaceholders)

        # Get some values
        ## cliargs
        _cliArgs = cliArgs if cliArgs != None else sys.argv
        ## startfile
        _startfile = "Unknown"
        for i,arg in enumerate(_cliArgs):
            if arg.strip().startswith("@startfile:"):
                __startfile = arg.split("@startfile:")[1] 
                if os.path.exists(__startfile):
                    _startfile = __startfile
                    _cliArgs.pop(i)
                else:
                    _cliArgs[i] = __startfile
        ## efile
        if os.path.exists(_cliArgs[0]):
            _efile = _cliArgs[0]
        else:
            _efile = "Unknown"
        _regionalVars["Args"] = _cliArgs
        _regionalVars["Startfile"] = _startfile
        _regionalVars["Efile"] = _efile

        # Define argparser
        _argparser = argparse.ArgumentParser(
            prog = "Crosshell",
            description = "Crosshell Modulo"
        )
        _regionalVars["Argparser"] = _argparser
        for arg in _arguments:
            _argparser.add_argument(*arg[0], **arg[1])
        _argparser.add_argument('additional', nargs='*', help="Unparsed arguments sent to crosshell.")

        # Parse args
        _regionalVars["Pargs"] = _argparser.parse_args(_cliArgs)

        # Handle placeholders in command and add stripansi
        cmdIndentifier = "cmd"
        aliasIndentifier = "stripAnsi"
        seenCmd = False
        seenAnsi = False
        for vl in _arguments:
            if vl[1]["dest"] == cmdIndentifier and seenCmd == False:
                for pl,val in _cmdArgPlaceholders.items():
                    setattr(_regionalVars["Pargs"], cmdIndentifier, getattr(_regionalVars["Pargs"], cmdIndentifier).replace(pl,val) )
                for i,arg in enumerate(_regionalVars["Args"]):
                    if arg in vl[0]:
                        if i+1 > len(_regionalVars["Args"])-1: pass
                        else:
                            for pl,val in _cmdArgPlaceholders.items():
                                _regionalVars["Args"][i+1] = _regionalVars["Args"][i+1].replace(val,pl)
                seenCmd = True
                break
        for vl in _arguments:
            if vl[1]["dest"] == aliasIndentifier and seenAnsi == False:
                _regionalVars["StripAnsi"] = getattr(_regionalVars["Pargs"], aliasIndentifier)
                seenAnsi = True
                break

        # Get CSlibDir
        _cslibdir = None
        if _regionalVars["RootPathRetrivalMode"] == "inspect":
            if os.path.exists( os.path.abspath(inspect.getfile(inspect.currentframe())) ):
                _cslibdir = os.path.dirname( os.path.abspath(inspect.getfile(inspect.currentframe())) )
            else:
                if os.path.dirname(__file__) == False:
                    _cslibdir = os.path.abspath( os.path.dirname(__file__) )
                else:
                    if os.path.exists(_regionalVars["Args"][0]):
                        _cslibdir = _regionalVars["Args"][0]
        else:
            if os.path.dirname(__file__) == False:
                _cslibdir = os.path.abspath( os.path.dirname(__file__) )
            else:
                if os.path.exists(_regionalVars["Args"][0]):
                    _cslibdir = _regionalVars["Args"][0]

        _regionalVars["CSlibDir"] = _cslibdir

        # Fix substituionTags
        tempSubstTagMan = tagSubstitionManager()
        hasPaths = ["CSlibDir"]
        def _hasTags(obj):
            hasTags = False
            if type(obj) == dict:
                for key,value in obj.items():
                    if _hasTags(value) == True:
                        hasTags = True
                        break
            elif type(obj) == list or type(obj) == "tuple":
                for i,value in enumerate(obj):
                    if _hasTags(value) == True:
                        hasTags = True
                        break
            elif type(obj) == str:
                if "{" in obj and "}" in obj:
                    hasTags = True
            return hasTags
        for key,value in _regionalVars.items():
            if _hasTags(value):
                hasPaths.append(key)
        def _applySubstTags(instance,obj,keyn="base"):
            if type(obj) == dict:
                for key,value in obj.items():
                    obj[key] = _applySubstTags(instance,value,key)
            elif type(obj) == list or type(obj) == "tuple":
                for i,value in enumerate(obj):
                    obj[i] = _applySubstTags(instance,value,keyn)
            elif type(obj) == str:
                value = normPathSepObj(absPathSepObj(tempSubstTagMan.eval(obj)))
                if keyn in hasPaths:
                    tempSubstTagMan.addTag(keyn,value)
                    obj = value
            return obj
        _regionalVars = _applySubstTags(tempSubstTagMan,_regionalVars)
        initSubstTags = {}
        for key,value in tempSubstTagMan.substTags.items():
            initSubstTags[self.storage.regionalPrefix+key] = value

        _regionalVars["PathTags"] = initSubstTags
        
        # Append possible custom
        if regionalVars != None: _regionalVars.update(regionalVars)

        # Normalize al paths in values
        _regionalVars = normPathSepObj(_regionalVars)

        # Apply
        self.regionalUpdate(_regionalVars)

        # Register things
        self.register("ptm", pathTagManager(initSubstTags))
        self.getregister("ptm").ensureAl()

        return self

    def start(self):
        """Starts the set prompt."""