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
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    else:
        return dictionary.get(keypath)

def setKeyPath(dictionary, keypath, value):
    '''CSlib.datafiles: Sets the value at a keypath from a dictionary (keypaths are keys sepparated by dots)'''
    keys = keypath.split('.')
    if len(keys) > 1:
        nested_dict = dictionary.copy()
        for key in keys[:-1]:
            if key not in nested_dict:
                nested_dict[key] = {}
            nested_dict = nested_dict[key]
        nested_dict[keys[-1]] = value
        return nested_dict
    else:
        nested_dict = dictionary.copy()
        nested_dict[keypath] = value
        return nested_dict
    
def setKeyPath(dictionary, keypath, value):
    '''CSlib.datafiles: Sets the value at a keypath from a dictionary (keypaths are keys sepparated by dots)'''
    # Split path by dots and put last pathPart as a part of value
    keypath = keypath.split(".")
    value = (keypath[-1], value)
    keypath.pop(-1)
    curr = dictionary
    for key in keypath:
        if key not in curr:
            curr[key] = {}
        curr = curr[key]
    k, v = value
    curr[k] = v
    return dictionary