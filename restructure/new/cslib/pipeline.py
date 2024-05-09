import json, pickle

# region: Validators
def isJsonOrCodeblock(inp=str):
    inp = inp.strip()
    if inp.startswith("{") and inp.endswith("}"):
        if inp.lstrip("{").rstrip("}").strip() == "":
            return "codeblock"
        try:
            json.loads(inp)
            return "json"
        except ValueError as e1:
            #try:
            #    json.loads(inp.replace("\\033","!ESC!"))
            #    return "json"
            #except ValueError as e2:
                return "codeblock"
    else:
        return False

def isJson(inp=str):
    if isJsonOrCodeblock(inp) == "json": return True
    else:
        return False

def isCodeblock(inp=str):
    if isJsonOrCodeblock(inp) == "codeblock": return True
    else:
        return False

def isInt(inp=str):
    return inp.isdigit()

def isFloat(inp=str):
    if ("." in inp and inp.replace(".","").isdigit()) or ("," in inp and inp.replace(",","").isdigit()):
        return True
    else:
        return False

def isList(inp=str):
    inp = inp.strip()
    if inp.startswith("[") and inp.endswith("]"):
        try:
            json.loads(inp)
            return True
        except ValueError:
            return False
    else:
        return False

def isPipeRaw(inp=str):
    if inp.strip().startswith("%piperaw%") and inp.strip().endswith("%piperaw%"):
        return True
    else:
        return False

# endregion: Validators

def determineDataType(inp) -> str:
    if type(inp) == str:
        if inp.lower() == "true": return "bool"
        elif inp.lower() == "false": return "bool"
        if inp.startswith('r"') and inp.endswith('"'):
            return "lit-str"
        t = isJsonOrCodeblock(inp)
        if t in ["json","codeblock"]: return t
        elif isList(inp) == True: return "list"
        elif isFloat(inp) == True: return "float"
        elif isInt(inp) == True: return "int"
        elif isPipeRaw(inp) == True: return "piperaw"
        else: return "str"
    elif isinstance(inp,varObj):
        return "varobj"
    else:
        return "python."+type(inp).__name__

def determineTypeForArgs(args=list) -> list:
    pairs = []
    for arg in args:
        pairs.append((arg,determineDataType(arg)))
    return pairs

def toStringAny(obj):
    type_ = type(obj)
    if type_ == tuple:
        obj,type_ = list(obj),list
    if type_ in [dict,list]:
        return json.dumps(obj)
    else:
        return str(obj)

class varObj():
    def __init__(self,name,value):
        self.name,self.value = name,value
        
class argumentHandler():
    """
    Class taking a list of arguments and parses through them.
    A list of the arguments are found under the .argv property,
    a list of the arguments in (<data>,<type>) pairs is found under the .targv property,
    and finally a list of data-type-evaluated arguments are found under the .pargv property.
    Note to escape a string being interprited as another datatype other them string, you can enclose like this: r"<arg>".
    ^ Has internaly the data-type 'lit-str' but gets parsed out to 'str'.
    """

    def __init__(self,arguments=list,serializerMode="dill"):
        self.serializerMode = serializerMode
        self.org = arguments
        # populate
        self.argv = []
        self.sargv = ""
        self.targv = []
        self.pargv = []
        if type(arguments) == list:
            for arg in arguments:
                self.sargv += toStringAny(arg) + " "
                if arg.startswith('r"') and arg.endswith('"'):
                    self.argv.append(arg.replace('r"',"",1).rstrip('"'))
                else:
                    self.argv.append(arg)
            self.sargv.rstrip(" ")
            self.targv = determineTypeForArgs(arguments)
            targv2 = []
            for arg in self.targv:
                self.pargv.append( self.objectify(*arg[::-1]) )
                if arg[1] == "lit-str":
                    arg = (arg[0].replace('r"',"",1).rstrip('"'),"str")
                targv2.append(arg)
            self.targv = targv2

    def serializeJson(self,obj):
        def serialize_property(prop):
            try:
                json.dumps(prop)
                return prop
            except TypeError:
                try:
                    return "§PICKLE§=" + str(pickle.dumps(prop).hex())
                except:
                    return "§STR§="+str(prop)
        if isinstance(obj, dict):
            return {key: self.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.serialize(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return {key: serialize_property(value) for key, value in obj.__dict__.items()}
        else:
            return serialize_property(obj)

    def deserializeJson(self,obj):
        if type(obj) == str:
            if obj.startswith("§PICKLE§="):
                obj = obj.replace("§PICKLE§=","",1)
                return pickle.loads(bytes.fromhex(obj))
            elif obj.startswith("§STR§="):
                return obj.replace("§STR§=","",1)
        else:
            des = object()
            for k,v in json.loads(obj).items():
                if v.startswith("§PICKLE§="):
                    v = v.replace("§PICKLE§=","",1)
                    v = pickle.loads(bytes.fromhex(v))
                elif v.startswith("§STR§="):
                    v = v.replace("§STR§=","",1)
                setattr(des, k, v)
            return des

    def serialize(self,obj):
        if self.serializerMode == "dill":
            try:
                import dill # local, should have been resolved by pip
                return dill.dumps(obj).hex()
            except:
                return pickle.dumps(obj).hex()
        elif self.serializerMode == "pickle":
            return pickle.dumps(obj).hex()
        else:
            return self.serializeJson(obj)

    def deserialize(self,obj):
        if self.serializerMode == "dill":
            try:
                import dill # local, should have been resolved by pip
                return dill.loads(bytes.fromhex(obj))
            except:
                return pickle.loads(bytes.fromhex(obj))
        elif self.serializerMode == "pickle":
            return pickle.loads(bytes.fromhex(obj))
        else:
            return self.deserializeJson(obj)

    def objectify(self,type_:str,obj:object) -> object:
        if type_ == "bool":
            if type(obj) == str:
                if obj.lower() == "true": return True
                elif obj.lower() == "false": return False
                else: return obj
            else:
                return obj
        elif type_ in ["python.int","int"]:
            return int(obj)
        elif type_ in ["python.float","float"]:
            return float(obj)
        elif type_ in ["python.str","str"]:
            return obj
        elif type_ in ["python.tuple","tuple"]:
            obj = obj.replace("(","[",1)
            obj = (obj[::-1].replace(")","]",1))[::-1]
            return json.loads(obj)
        elif type_ in ["python.list","list","dict","json"]:
            return json.loads(obj)
        elif type_ == "piperaw":
            return self.deserialize((obj.replace("%piperaw%","",1)[::-1].replace("%warepip%","",1))[::-1].strip())
        elif type_ == "lit-str":
            return obj.replace('r"',"",1).rstrip('"')
        elif type_ == "varobj":
            return obj.value
        else:
            return obj
        
    def determineDt(self,arg:object) -> str:
        return determineDataType(arg)

    def popSargv(self,ind):
        """Pops an index from sArgv by splitting by space, poping the index and joining back."""
        l = self.sargv.split(" ")
        l.pop(ind)
        self.sargv = ' '.join(l)
        del l
    def popArgv(self,ind):
        """Pops an index from the argv list."""
        self.argv.pop(ind)
    def popTargv(self,ind):
        """Pops an index from the targv list."""
        self.targv.pop(ind)
    def popPargv(self,ind):
        """Pops an index from the pargv list."""
        self.pargv.pop(ind)
    def popAl(self,ind):
        """Pops an index from sargv, argv, targv and pargv, note sargv popping is handled by splitting by space, popping and rejoining."""
        self.popSargv(ind)
        self.popArgv(ind)
        self.popTargv(ind)
        self.popPargv(ind)
    
    def removeSargv(self,val=str):
        """Removes a value from sargv, by splitting by space, removing the value and rejoining."""
        l = self.sargv.split(" ")
        l.remove(val)
        self.sargv = ' '.join(l)
        del l
    def replaceSargv(self,old=str,new="",amnt=None):
        """Replaces a substring in sargv."""
        if amnt != None and type(amnt) == int:
            self.sargv = self.sargv.replace(old,new,amnt)
        else:
            self.sargv = self.sargv.replace(old,new)
    def removeArgv(self,val):
        """Removes a value from argv."""
        self.argv.remove(val)
    def removeTargv(self,val=tuple):
        """Removes a value from targv, taking a tuple of ("<type>",<val>)"""
        self.targv.remove(val)
    def removeTargvAnyType(self,type_=str):
        """Removes any entry with a type from targv."""
        l = self.targv
        for i,x in enumerate(l):
            if x[1] == type_:
                self.targv.remove(x)
        del l
    def removeTargvAnyVal(self,val):
        """Removes any entry with a value from targv."""
        l = self.targv
        for i,x in enumerate(l):
            if x[0] == val:
                self.targv.remove(x)
        del l
    def removePargv(self,val):
        """Removes a value from pargv."""
        self.pargv.remove(val)
    def removeAl(self,val):
        """Removes a value from sargv if its a string, argv, targv but any value match and pargv."""
        if type(val) == str:
            self.removeSargv(val)
        self.removeArgv(val)
        self.removeTargvAnyVal(val)
        self.removePargv(val)

def returner(*args,**kwargs):
    """
    Function that can be used from inside a cmdlet to "export" variables or data to the pipeline,
    print would still be picked up unless disabled but this acts as a way to export anything.
    """
    toExport = args
    for k,v in kwargs.items():
        toExport.append( varObj(k,v) )
    toExport_prepped = []
    for arg in toExport:
        type_ = type(arg)
        if type_ in [str,int,float]:
            arg = str(arg)
        elif type_ == tuple:
            arg = str(list(arg))
        elif type_ == list:
            arg = str(arg)
        elif type_ == dict:
            arg = json.dumps(arg)
        else:
            deser = ""
            try:
                import dill # local, should have been resolved by pip
                deser = dill.dumps(arg).hex()
            except:
                deser = pickle.dumps(arg).hex()
            arg = "%piperaw%"+deser+"%piperaw%"
        toExport_prepped.append(arg)
    # Push to pipeline

def _interactiveTest():
    import os
    print("DtDt, use :x to exit and :c to clear.")
    while True:
        i = input("> ")
        if i.lower() == ":x": exit()
        elif i.lower() == ":c": os.system("CLS")
        else:
            if i.startswith("!"):
                i = i.replace("!","",1)
                print(determineTypeForArgs(i.split(";")))
            else:
                print(determineDataType(i))
