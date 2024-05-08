import json, re, os
from cslib.piptools import autopipImport
from cslib.commentParsing import _stripJsonComments, extractComments_v2, injectComments_v2, extractComments_newlineSupport, injectComments_newlineSupport
from cslib.pathtools import normPathSep,normPathSepObj
from cslib.commentParsing import finBet,finBetWl
import yaml

try:
    import yaml
except:
    yaml = autopipImport("yaml","pyyaml")

'''
CSlibs: Datafiles module, contains a jsonYamlProvider class for using such files with more ease
Depends on pyyaml

'''

def _fileHandler(mode,operation,file,content=None,encoding="utf-8",safeSeps=False,yaml_sort=False,readerMode="Off",commentsToInclude=None,discardNewlines=False,fileIsStream=False):
    """CSlib.datafiles: INTERNAL, abstraction layer for json/yaml files.
    
    readerMode: 'Off'/'Comments'/'Newline'
    
    discardNewlines: Only works with readerMode 'Comments'"""
    if readerMode.lower() == "off":
        readerMode = False
        readerEx = None
        readerIn = None
    elif readerMode.lower() == "comments":
        readerMode = True
        readerEx = extractComments_v2
        readerIn = injectComments_v2
    elif readerMode.lower() == "newline":
        readerMode = True
        readerEx = extractComments_newlineSupport
        readerIn = injectComments_newlineSupport
    if fileIsStream != True:
        if not os.path.exists(file):
            file = normPathSepObj(file)
    if mode == "json":
        if operation == "get":
            if fileIsStream == True:
                content = _stripJsonComments(file.read())
                if content == "" or content == None:
                    content = "{}"
            else:
                content = _stripJsonComments(open(file,'r',encoding=encoding).read())
            if readerMode != False:
                if readerMode.lower() == "comments":
                    content,extractedComments = readerEx(content,discardNewlines)
                else:
                    content,extractedComments = readerEx(content)
            _dict = json.loads(content)
            if safeSeps == True: return normPathSepObj(_dict)
            else:
                if readerMode != False:
                    return _dict,extractedComments
                else:
                    return _dict
        elif operation == "set":
            content_str = json.dumps(content)
            if readerMode != False and commentsToInclude != None and type(commentsToInclude) == dict:
                if readerMode.lower() == "comments":
                    content_str = readerIn(content_str.split("\n"), commentsToInclude, discardNewlines)
                else:
                    content_str = readerIn(content_str, commentsToInclude, discardNewlines)
            if fileIsStream == True:
                file.write(content_str)
            else:
                open(file,'w',encoding=encoding).write(content_str)
    elif mode == "yaml":
        if operation == "get":
            if fileIsStream == True:
                content = _stripJsonComments(file.read())
            else:
                content = _stripJsonComments(open(file,'r',encoding=encoding).read())
            if readerMode != False:
                if readerMode.lower() == "comments":
                    content,extractedComments = readerEx(content,discardNewlines)
                else:
                    content,extractedComments = readerEx(content)
            _dict = yaml.safe_load(content)
            if safeSeps == True: return normPathSepObj(_dict)
            else:
                if readerMode != False:
                    return _dict,extractedComments
                else:
                    return _dict
        elif operation == "set":
            content_str = yaml.dump(content, sort_keys=yaml_sort)
            if readerMode != False and commentsToInclude != None and type(commentsToInclude) == dict:
                if readerMode.lower() == "comments":
                    content_str = readerIn(content_str.split("\n"), commentsToInclude, discardNewlines)
                else:
                    content_str = readerIn(content_str, commentsToInclude, discardNewlines)
            if fileIsStream == True:
                file.write(content_str)
            else:
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

# DOTFILE
def countIndent(s):
    spaceCount = 0
    for char in s:
        if char == ' ':
            spaceCount += 1
        elif char == '\t':
            # Assuming each tab is equivalent to four spaces
            spaceCount += 4
        else:
            # If a non-space or non-tab character is encountered, stop counting
            break
    return spaceCount

def revStackObj(obj,mlStrStackFormat="§STACK:MLSTR:%§",jsonStackFormat="§STACK:JSON:%§",mlStrStack=list,jsonStack=list,mlP='@"',mlS='"@',jsP=None,jsS=None):
    if type(obj) == dict:
        for k,v in obj.items():
            obj[revStackObj(k,mlStrStackFormat,jsonStackFormat,mlStrStack,jsonStack,mlP,mlS,jsP,jsS)] = revStackObj(v,mlStrStackFormat,jsonStackFormat,mlStrStack,jsonStack,mlP,mlS,jsP,jsS)
    elif type(obj) in [list,tuple]:
        for i in range(len(obj)):
            obj[i] = revStackObj(obj[i],mlStrStackFormat,jsonStackFormat,mlStrStack,jsonStack,mlP,mlS,jsP,jsS)
    elif type(obj) == str:
        if ':'.join(obj.strip().rstrip("§").split(":")[:-1]) == jsonStackFormat.split("%")[0].rstrip(":"):
            i = int(obj.strip().rstrip("§").split(":")[-1])
            obj = json.loads(jsonStack[i].replace("§nl§","\n"))
        else:
            for i in range(len(mlStrStack)):
                nv = mlStrStack[i].replace("§nl§","\n")
                if mlP != None: nv = nv.lstrip(mlP)
                if mlS != None: nv = nv.rstrip(mlS)
                obj = obj.replace( mlStrStackFormat.replace("%",str(i)), nv, 1 )
            for i in range(len(jsonStack)):
                nv = jsonStack[i].replace("§nl§","\n")
                if jsP != None: nv = nv.lstrip(jsP)
                if jsS != None: nv = nv.rstrip(jsS)
                obj = obj.replace( jsonStackFormat.replace("%",str(i)), nv, 1 )
    return obj

def nameSpaceHandler(data=dict):
    nameSpaceData = {
        "Default": {}
    }
    for k,v in data.items():
        if ":" in k:
            nameSpace = k.split(":")[0]
            k = ":".join(k.split(":")[1:])
            if nameSpaceData.get(nameSpace) == None: nameSpaceData[nameSpace] = {}
            nameSpaceData[nameSpace][k] = v
        else:
            nameSpaceData["Default"][k] = v
    return nameSpaceData 

def rudaDotfile_to_dict(content,commentChars="#",escapor="\\",sectionChars="≈≈",headingChars="[]"):
    """
    Converts rudamentary-dotfile formats to a dictionary handling comments, namespaces and headed-sections.
    Takes:
      content: str,
      commentChars: str, (1 or 2, first char is prefix, second is suffix)
      escapor: str, (1 len)
      sectionChars: str, (1 or 2, first char is prefix, second is suffix)
      headingChars: str, (1 or 2, first char is prefix, second is suffix)

    [Format]:

        # Comments prefixed like this

        ≈≈≈≈≈≈≈≈[Section-Name]≈≈≈≈≈≈≈≈

        The amount of ≈ dosen't matter.

        <Key> = <Value>
            /
        <NameSpace>:<Key> = <Value>

        <Key> = {<JSON_W_LINES>}
            /
        <NameSpace>:<Key> = {<JSON_W_LINES>}
        
        <Key> = [...]
            /
        <NameSpace>:<Key> = [...]

        <Key> = @"<MultiLineString>"@

        Indentation Is Ignored unless inside multilinestring.
        

    [Example]:
    
        # This is an example
        ≈[Conf.DotFile]≈ # Note the use of "Conf." this will change the syntax of bellow to be <key>:<value> instead of using =
        Format: 1
        Author: SimonKalmiClaesson
        Description: # Note that the bellow code uses indents to determine "parent/key" this is only when section is prefixed with "Conf."
        This file contains some example rudamentary-dotfile code.
        Wabba dabba do!
        
        # Lets add a section with the name raw that sets the "raw" variable under the "autofill" namespace
        ≈[Raw]≈
        autofill:raw = {
            "jsonKey": "jsonVal"
        }

        ≈[CustomSection]≈
        CustomVar = CustomVal
        CustomNameSpace:CustomVar = CustomVal


    [ReturnedAs]:
        {
          "<Section>": {
            "<NameSpace>": {
              "<VariableName>": "<VariableValue>"
            }
          }
        }

        'Default' is a prefilled section and namespace.
    """
    # Strip comments
    commentStrippedLines = []
    if len(commentChars[0]) > 1:
        st = commentChars[0]
        en = commentChars[1]
    else:
        st = commentChars[0] 
        en = None
    for line in content.split("\n"):
        line = line.replace(escapor+st,st+"STPL"+st)
        if en != None: line = line.replace(escapor+en,en+"ENPL"+en)
        if en != None:
            # parse
            if st in line and en in line:
                prem = finBet(line,st,en)
                line = line.replace(prem,"")
                if line.strip() != "":
                    line = line.replace(st+"STPL"+st,escapor+st)
                    line.replace(en+"ENPL"+en,escapor+en)
                    commentStrippedLines.append(line)
            else:
                line = line.replace(st+"STPL"+st,escapor+st)
                line.replace(en+"ENPL"+en,escapor+en)
                commentStrippedLines.append(line)
        else:
            st = commentChars[0]
            # parse
            if st in line:
                line = line.split(st)[0]
            if not line.lstrip().startswith(st):
                line = line.replace(st+"STPL"+st,escapor+st)
                commentStrippedLines.append(line)
    # Figure out sections
    sectionedLines = {
        "Default": {
            "isConf": False,
            "lines": [],
            "data": {}
        }
    }
    if len(sectionChars) > 1:
        st = sectionChars[0]
        en = sectionChars[1]
    else:
        st = sectionChars[0]
        en = None
    if len(headingChars) > 1:
        st2 = headingChars[0]
        en2 = headingChars[1]
    else:
        st2 = headingChars[0]
        en2 = None
    inSection = "Default"
    stack_mlstr = []
    stack_json = []
    commentStrippedLines_,stack_ = finBetWl('§nl§'.join(commentStrippedLines), '@"','"@', "§STACK:MLSTR:%§",0)
    commentStrippedLines = commentStrippedLines_.split("§nl§")
    stack_mlstr.extend(stack_)
    commentStrippedLines_,stack_ = finBetWl('§nl§'.join(commentStrippedLines), '{','}', "§STACK:JSON:%§",0)
    commentStrippedLines = commentStrippedLines_.split("§nl§")
    stack_json.extend(stack_)
    for line in commentStrippedLines:
        sectionName = None
        if en != None:
            if line.lstrip().startswith(st) and line.rstrip().endswith(en):
                if en2 != None:
                    if st2 in line and en2 in line:
                        sectionName = finBet(line,st2,en2).lstrip(st2).rstrip(en2)
                else:
                    if st2 in line:
                        sectionName = en.join(st2.join(line.split(st2)[1:]).split(en)[:-1])
                if sectionName != None:
                    inSection = sectionName
            else:
                if inSection != None:
                    if inSection.startswith("Conf."):
                        isConf = True
                        inSection = inSection.replace("Conf.","",1)
                    elif inSection.startswith("conf."):
                        isConf = True
                        inSection = inSection.replace("conf.","",1)
                    else: isConf = False
                    if sectionedLines.get(inSection) == None: sectionedLines[inSection] = {
                        "isConf": isConf,
                        "lines": [],
                        "data": {}
                    }
                    sectionedLines[inSection]["lines"].append(line)
        else:
            if line.lstrip().startswith(st):
                if en2 != None:
                    if st2 in line and en2 in line:
                        sectionName = finBet(line,st2,en2).lstrip(st2).rstrip(en2)
                else:
                    if st2 in line:
                        sectionName = st2.join(line.split(st2)[1:])
            else:
                if inSection != None:
                    if inSection.startswith("Conf."):
                        isConf = True
                        inSection = inSection.replace("Conf.","",1)
                    elif inSection.startswith("conf."):
                        isConf = True
                        inSection = inSection.replace("conf.","",1)
                    else: isConf = False
                    if sectionedLines.get(inSection) == None: sectionedLines[inSection] = {
                        "isConf": isConf,
                        "lines": [],
                        "data": {}
                    }
                    sectionedLines[inSection].append(line)
    # Parse the lines
    for sName,section in sectionedLines.items():
        lines = section["lines"]
        ## isConf == True
        if section["isConf"] == True:
           sectionedLines[sName]["data"] = yaml.safe_load('\n'.join(lines))
        ## isConf == False
        if section["isConf"] == False:
            sectionedLines[sName]["data"] = config_to_dict('\n'.join(lines))
    # Re-replace Stack items
    sectionedLines = revStackObj( sectionedLines, "§STACK:MLSTR:%§", "§STACK:JSON:%§", stack_mlstr, stack_json )
    # Parse namespaces
    parsedData = {}
    for sName,section in sectionedLines.items():
        parsedData[sName] = nameSpaceHandler(sectionedLines[sName]["data"])
    return parsedData