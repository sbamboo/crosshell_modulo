import json,re,os
from .cslib import normalizePathSepMT,intpip

try:
    import yaml
except:
    intpip("install pyyaml")
    import yaml

'''
CSlibs: Datafiles module, contains a jsonYamlProvider class for using such files with more ease
Depends on pyyaml

'''

def injectStringAtIndex(dictionary, index, string_to_inject):
    # Create a list to store the dictionary items as (index, value) tuples
    items = list(dictionary.items())
    # Insert the new key-value pair at the specified index
    items.insert(index, (index, string_to_inject))
    # Iterate over the remaining items and increment their keys
    for i in range(index + 1, len(items)):
        old_key, value = items[i]
        new_key = old_key + 1
        items[i] = (new_key, value)
    # Convert the modified list of items back to a dictionary
    modified_dict = dict(items)
    return modified_dict

def injectStringAtIndex(listToInjectTo=list,index=int,string=str) -> list:
    return listToInjectTo[:index] + [string] + listToInjectTo[index:]

def extractComments(json_or_yaml_string=str) -> (str,dict):
    if json_or_yaml_string != None:
        split = json_or_yaml_string.split("\n")
        newsplit = []
        extractedLines = {}
        split2 = []
        for elem in split:
            if elem.strip(" ") != "":
                split2.append(elem)
        split = split2
        for i,line in enumerate(split):
            strip = line.strip(" ")
            if strip.startswith("#") or strip.startswith("//"):
                extractedLines[i] = line
            else:
                newsplit.append(line)
        new = '\n'.join(newsplit)
        return new,extractedLines
    else:
        return json_or_yaml_string,None

def injectComments(json_or_yaml_string,extractedLines) -> str:
    if json_or_yaml_string != None and extractedLines != None and extractedLines != {}:
        split = json_or_yaml_string.split("\n")
        for i,line in extractedLines.items():
            split = injectStringAtIndex(split,i,line)
        return '\n'.join(split)
    else:
        return json_or_yaml_string

def extractComments_newlineSupport(json_or_yaml_string=str) -> (str,dict):
    if json_or_yaml_string != None:
        split = json_or_yaml_string.split("\n")
        newsplit = []
        extractedLines = {}
        for i,elem in enumerate(split):
            if elem == "":
                split[i] = "§newline§"
        for i,line in enumerate(split):
            strip = line.strip(" ")
            if strip.startswith("#") or strip.startswith("//"):
                extractedLines[i] = line
            elif strip == "§newline§":
                extractedLines[i] = "\n"
            else:
                newsplit.append(line)
        new = '\n'.join(newsplit)
        return new,extractedLines
    else:
        return json_or_yaml_string,None

def injectComments_newlineSupport(json_or_yaml_string,extractedLines) -> str:
    if json_or_yaml_string != None and extractedLines != None and extractedLines != {}:
        split = json_or_yaml_string.split("\n")
        for i,line in extractedLines.items():
            split = injectStringAtIndex(split,i,line)
        newstring = ""
        for elem in split:
            if elem != "\n":
                newstring += "\n" + elem
            else:
                newstring += elem
        return newstring.strip("\n")
    else:
        return json_or_yaml_string

def _stripJsonComments(jsonString):
    commentPattern = r'(\/\/[^\n]*|\/\*[\s\S]*?\*\/)'
    jsonWithoutComments = re.sub(commentPattern, '', jsonString)
    return jsonWithoutComments

def _fileHandler(mode,operation,file,content=None,encoding="utf-8",safeSeps=False,yaml_sort=False,keepComments=False,commentsToInclude=None,newlineSupport=False):
    '''CSlib.datafiles: INTERNAL, abstraction layer for json/yaml files.'''
    if not os.path.exists(file):
        file = normalizePathSepMT(file)
    if mode == "json":
        if operation == "get":
            content = _stripJsonComments(open(file,'r',encoding=encoding).read())
            if keepComments == True:
                if newlineSupport == True:
                    content,extractedComments = extractComments_newlineSupport(content)
                else:
                    content,extractedComments = extractComments(content)
            _dict = json.loads(content)
            if safeSeps == True: return normalizePathSepMT(_dict)
            else:
                if keepComments == True:
                    return _dict,extractComments
                else:
                    return _dict
        elif operation == "set":
            content_str = json.dumps(content)
            if keepComments == True and commentsToInclude != None and type(commentsToInclude) == dict:
                if newlineSupport == True:
                    content_str = injectComments_newlineSupport(content_str, commentsToInclude)
                else:
                    content_str = injectComments(content_str, commentsToInclude)
            open(file,'w',encoding=encoding).write(content_str)
    elif mode == "yaml":
        if operation == "get":
            content = open(file, "r",encoding=encoding).read()
            if keepComments == True:
                if newlineSupport == True:
                    content,extractedComments = extractComments_newlineSupport(content)
                else:
                    content,extractedComments = extractComments(content)
            _dict = yaml.safe_load(content)
            if safeSeps == True: return normalizePathSepMT(_dict)
            else:
                if keepComments == True:
                    return _dict,extractedComments
                else:
                    return _dict
        elif operation == "set":
            content_str = yaml.dump(content, sort_keys=yaml_sort)
            if keepComments == True and commentsToInclude != None and type(commentsToInclude) == dict:
                if newlineSupport == True:
                    content_str = injectComments_newlineSupport(content_str, commentsToInclude)
                else:
                    content_str = injectComments(content_str, commentsToInclude)
            open(file,'w',encoding=encoding).write(content_str)

class jsonYamlProviderSimpleIO():
    '''
    CSlib.datafiles: Json/Yaml provider, allowes you to quickely use get and set methods on the files
    OnInit:
      takes: mode of string, being "json" or "yaml"
      file:  string filepath/filename if applicable
      encoding: file encoding
      yaml_sort: Whether or not the yaml mode should ABC sort the file
      keepComments: If fileHandler should keep comments in file (experimental)
    '''
    def __init__(self,mode=str,file=str,encoding="utf-8",yaml_sort=True,keepComments=False):
        self.mode = mode
        self.file = file
        self.encoding = encoding
        self.yaml_sort = yaml_sort
        self.keepComments = keepComments
        self.commentsToInclude = commentsToInclude
    def set(self,value,key=None,commentsToInclude=None):
        if key == None:
            if self.keepComments == True:
                _fileHandler(self.mode,"set",self.file,value,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True,commentsToInclude=commentsToInclude)
            else:
                _fileHandler(self.mode,"set",self.file,value,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
        else:
            if self.keepComments == True:
                data,comments = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True)
                data[key] = value
                _fileHandler(self.mode,"set",self.file,data,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True,commentsToInclude=commentsToInclude)
            else:
                data = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
                data[key] = value
                _fileHandler(self.mode,"set",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
    def get(self):
        if self.keepComments == True:
            data,comments = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True)
        else:
            data = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
            comments = None
        return data,comments

class jsonYamlProvider():
    '''
    CSlib.datafiles: Json/Yaml provider, allowes you to use a file as a dictionary
    OnInit:
      takes: mode of string, being "json" or "yaml"
      file:  string filepath/filename if applicable
      encoding: file encoding
      yaml_sort: Whether or not the yaml mode should ABC sort the file
      keepComments: If fileHandler should keep comments in file (experimental)
    '''
    def __init__(self,mode=str,file=str,encoding="utf-8",yaml_sort=True,keepComments=False):
        self.mode = mode
        self.file = file
        self.encoding = encoding
        self.yaml_sort = yaml_sort
        self.keepComments = keepComments
    def _get(self):
        if self.keepComments == True:
            data,comments = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True)
            return data,comments
        else:
            data = _fileHandler(self.mode,"get",self.file,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
            return data,None
    def _set(self,data,commentsToInclude=None):
        if self.keepComments == True:
            _fileHandler(self.mode,"set",self.file,data,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=True,commentsToInclude=commentsToInclude)
        else:
            _fileHandler(self.mode,"set",self.file,data,encoding=self.encoding,yaml_sort=self.yaml_sort,keepComments=False)
    def __setitem__(self, key, value):
        data,comments = self._get()
        data.__setitem__(key, value)
        self._set(data,comments)
    def __ior__(self, other):
        if isinstance(other, dict):
            data,comments = self._get()
            data.update(other)
            self._set(data,comments)
        return self
    def __getitem__(self, key):
        data,comments = self._get()
        if self.keepComments == True:
            return data.__getitem__(key),comments
        else:
            return data.__getitem__(key)
    def append(self,data):
        _data,comments = self._get()
        _data.append(data)
        self._set(_data,comments)
    def update(self,data):
        _data,comments = self._get()
        _data.update(data)
        self._set(_data,comments)
    def get(self,key=None):
        data,comments = self._get()
        if key != None:
            if self.keepComments == True:
                return data[key],comments
            else:
                return data[key]
        else:
            if self.keepComments == True:
                return data,comments
            else:
                return data
    def clear(self):
        _data,comments = self._get()
        _data.clear()
        self._set(_data)

def getKeyPath(dictionary, keypath, listAs1Elem=False):
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
                    if listAs1Elem == True:
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

#TODO: Test
def remKeyPath(dictionary, keypath):
    '''CSlib.datafiles: Removes the value at the specified keypath from a dictionary (keypaths are keys separated by dots)'''
    keys = keypath.split('.')
    if len(keys) > 1:
        blacklist = []  # To keep track of keys that should be skipped
        parent = dictionary
        last_key = None
        # Traverse the dictionary to find the parent of the last key
        for i, key in enumerate(keys):
            if i not in blacklist:
                try:
                    key = int(key)
                except ValueError:
                    pass
                
                if i < len(keys) - 1:
                    if isinstance(parent, dict) and key in parent:
                        parent = parent[key]
                    elif isinstance(parent, list) and 0 <= key < len(parent):
                        parent = parent[key]
                    else:
                        # Key not found, nothing to remove
                        return dictionary  # Return the original dictionary unchanged
                else:
                    last_key = key
        # Check if the parent is a list or dictionary and remove the last key
        if isinstance(parent, list) and 0 <= last_key < len(parent):
            parent.pop(last_key)
        elif isinstance(parent, dict) and last_key in parent:
            del parent[last_key]
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
    for line in config_file_content.split("\n"):
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=')
            value = value.strip()
            if value == '""': value = None
            if value == '[]': value = None
            if value != None:
                if "[" in value and "]" in value:
                    try:
                        value = json.loads(value)
                    except:
                        value = value.replace("[","").replace("]","").split(",")
                if type(value) == list:
                    newValue = []
                    for k in value:
                        k = k.replace('"',"")
                        newValue.append(k)
                    value = newValue
                else:
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                if type(value) == str:
                    value = value.replace('"',"")
            config_dict[key.strip()] = value
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