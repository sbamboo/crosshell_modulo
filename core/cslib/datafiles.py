import json,yaml

'''
CSlibs: Datafiles module, contains a jsonYamlProvider class for using such files with more ease
Depends on pyyaml

'''

def _fileHandler(mode,operation,file,content=None):
    '''CSlib.datafiles: INTERNAL, abstraction layer for json/yaml files.'''
    if mode == "json":
        if operation == "get":
            return json.loads(open(file,'r').read())
        elif operation == "set":
            with open(file, "w") as outfile:
                json.dump(content, outfile)
    elif mode == "yaml":
        if operation == "get":
            with open(file, "r") as outfile:
                return yaml.safe_load(outfile)
        elif operation == "set":
            with open(file, "w") as outfile:
                yaml.dump(content, outfile)

class jsonYamlProviderSimpleIO():
    '''
    CSlib.datafiles: Json/Yaml provider, allowes you to quickely use get and set methods on the files
    OnInit:
      takes: mode of string, being "json" or "yaml"
      file:  string filepath/filename if applicable
    '''
    def __init__(self,mode=str,file=str):
        self.mode = mode
        self.file = file
    def set(self,value,key=None):
        if key == None:
            _fileHandler(self.mode,"set",self.file,value)
        else:
            data = _fileHandler(self.mode,"get",self.file)
            data[key] = value
            _fileHandler(self.mode,"set",self.file,data)
    def get(self):
        return _fileHandler(self.mode,"get",self.file)

class jsonYamlProvider():
    '''
    CSlib.datafiles: Json/Yaml provider, allowes you to use a file as a dictionary
    OnInit:
      takes: mode of string, being "json" or "yaml"
      file:  string filepath/filename if applicable
    '''
    def __init__(self,mode=str,file=str):
        self.mode = mode
        self.file = file
    def __setitem__(self, key, value):
        data = _fileHandler(self.mode,"get",self.file)
        data.__setitem__(key, value)
        _fileHandler(self.mode,"set",self.file,data)
    def __ior__(self, other):
        if isinstance(other, dict):
            data = _fileHandler(self.mode,"get",self.file)
            data.update(other)
            _fileHandler(self.mode,"set",self.file,data)
        return self
    def __getitem__(self, key):
        data = _fileHandler(self.mode,"get",self.file)
        return data.__getitem__(key)
    def append(self,data):
        data = _fileHandler(self.mode,"get",self.file)
        data.append(data)
        _fileHandler(self.mode,"set",self.file,data)
    def update(self,data):
        data = _fileHandler(self.mode,"get",self.file)
        data.update(data)
        _fileHandler(self.mode,"set",self.file,data)
    def get(self,key=None):
        data = _fileHandler(self.mode,"get",self.file)
        if key != None:
            return data[key]
        else:
            return data
    def clear(self):
        data = _fileHandler(self.mode,"get",self.file)
        data.clear()
        _fileHandler(self.mode,"set",self.file,data)

def getKeyPath(dictionary, keypath):
    '''CSlib.datafiles: Gets the value at a keypath from a dictionary (keypaths are keys sepparated by dots)'''
    keys = keypath.split('.')
    if len(keys) > 1:
        value = dictionary
        try:
            blacklist = []
            for i,key in enumerate(keys):
                if i not in blacklist:
                    try: key = int(key)
                    except: pass
                    value = value[key]
            # Fix for string expectancy rather then list
            if type(value) == list:
                try:
                    index = int(keys[i+1])
                    value = value[index]
                    blacklist.append(i+1)
                except:
                    value = value[0]
            return value
        except (KeyError, TypeError):
            return None
    else:
        return dictionary.get(keypath)

#TODO: Reimplement
def setKeyPath(dictionary, keypath, value, nonAppend=False, update=False):
    '''CSlib.datafiles: Sets the value at a keypath from a dictionary (keypaths are keys sepparated by dots)'''
    if update == True: nonAppend = True
    ogKeypath = keypath
    # Split path by dots and put last pathPart as a part of value
    keypath = keypath.split(".")
    value = (keypath[-1], value)
    keypath.pop(-1)
    curr = dictionary
    block = False
    for i,key in enumerate(keypath):
        if key not in curr:
            curr[key] = {}
        if type(curr[key]) == str:                       # Fix for subproperty of existing string
            curr[key] =  [curr[key],{value[0]:value[1]}] #
        elif type(curr[key]) == list:                 # Fix for getting a list
            try:
                index = int(value[0])
                curr[key][index] = value[1]
            except:
                if {value[0]:value[1]} not in curr[key]:  # Fix for subproperty of existing string
                    curr[key].append({value[0]:value[1]}) #
                    block = True
        else:
            curr = curr[key]
    k, v = value
    if nonAppend == True:
        if update == True and curr.get(k) != None:
            if type(curr[k]) == list:
                if v not in curr[k]:
                    curr[k].extend(v)
            else:
                curr[k].update(v)
        else:
            if block == False:
                fkp = (".".join(ogKeypath.split(".")[:-1]))
                tv = getKeyPath(dictionary, f"{fkp}.1")
                if tv == None:
                    curr[k] = v
    else:
        if curr.get(k) == {} or curr.get(k) == None:
            try:
                index = int(k)
                if type(curr) == list:
                    curr[int(k)] = v
            except:
                if block == False:
                    curr.update({k: v})
    return dictionary

# .Config
def config_to_dict(config_file_content=str) -> dict:
    """
    Convert the .config or .cfg file-format to a dictionary.

    Parameters:
    config_file_content (str): The configuration file content.

    Returns:
    dict: A dictionary representing the configuration.
    """
    config_dict = {}
    for line in config_file_content:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=')
            config_dict[key.strip()] = value.strip()
    return config_dict

def dict_to_config(config_dict=dict) -> str:
    """
    Convert a dictionary to the .config or .cfg file-format.

    Parameters:
    config_dict (dict): The dictionary containing configuration data.

    Returns:
    str: config file content.
    """
    config_content = ""
    for key, value in config_dict.items():
        config_content += f"{key}={value}\n"
    return config_content