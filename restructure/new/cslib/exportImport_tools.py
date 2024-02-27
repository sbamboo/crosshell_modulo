import pickle, inspect

def _noneTypeIdentityFunc(string):
    return string
noneTypeIdentityFunc = _noneTypeIdentityFunc

def getArgsForFunc(func_var):
    argspec = inspect.getfullargspec(func_var)
    return {
        "args": argspec.args,
        "defa": argspec.defaults,
        "varargs": argspec.varargs,
        "varkwargs": argspec.varkw,
        "asocdefa": zip(argspec.args[-len(argspec.defaults):], argspec.defaults)
    }

class UnserializableObjectReference():
    def __init__(self,reference=str):
        self.static = str(f'<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))}, referencing: <{reference.__class__.__module__}.{reference.__class__.__name__} object at {hex(id(reference))}>>')
        del reference
    def __repr__(self):
        return self.static

def argParse_to_dict(instance,parsed,orgArgs=None):
    _prop_names = [
        'prog',
        'usage',
        'description',
        'formatter_class',
        'conflict_handler',
        'add_help',
    ]
    _action_prop_names = [
            'option_strings',
            'dest',
            'nargs',
            'const',
            'default',
            'type',
            'choices',
            'required',
            'help',
            'metavar',
        ]
    export = {
        "main": {
            "class": instance.__class__,
            "props": {}
        },
        "actions": [],
        "parsed": [],
        "orgArgs": orgArgs,
        "identityTypeInstance": None
    }
    for _prop in _prop_names:
        export["main"]["props"][_prop] = getattr(instance, _prop)
    for action in instance._actions:
        if action.__class__.__name__ not in ["_HelpAction"]:
            actionDict = {
                "class": action.__class__,
                "props": {}
            }
            for _prop in _action_prop_names:
                actionDict["props"][_prop] = getattr(action, _prop)
            export["actions"].append(actionDict)
    export["parsed"] = parsed

    firstInstanceType = list(instance._registries["type"].keys())[0]
    if firstInstanceType == None:
        export["identityTypeInstance"] = (None,noneTypeIdentityFunc)
        instance._registries["type"][firstInstanceType] = UnserializableObjectReference(instance._registries["type"][firstInstanceType])
    else:
        try:
            _ = pickle.dumps(
                instance._registries["type"][firstInstanceType]
            )
            export["identityTypeInstance"] = (firstInstanceType,instance._registries["type"][firstInstanceType])
            instance._registries["type"][firstInstanceType] = UnserializableObjectReference(instance._registries["type"][firstInstanceType])
        except:
            export["identityTypeInstance"] = (None,noneTypeIdentityFunc)
            instance._registries["type"][firstInstanceType] = UnserializableObjectReference(instance._registries["type"][firstInstanceType])
            

    return export

def initClassWithProps(class_,props,safe=False):
    if safe == True:
        argsValid = getArgsForFunc(class_.__init__)
        valArgs = argsValid["args"]
        for dk,dv in argsValid["asocdefa"]:
            if dk not in valArgs: valArgs.append(dv)
        nprops = {}
        for k,v in props.items():
            if k in valArgs:
                nprops[k] = v
        props = nprops
    return class_(**props)


def argParse_from_dict(import_,reparse=False,safeCreation=True):
    # create main
    #parser = import_["main"]["class"](**import_["main"]["props"])
    parser = initClassWithProps(import_["main"]["class"],import_["main"]["props"],safe=safeCreation)
    for act in import_["actions"]:
        #actObj = act["class"](**act["props"])
        actObj = initClassWithProps(act["class"],act["props"],safe=safeCreation)
        parser._add_action(actObj)
    parsed = []
    if reparse == True and import_.get("orgArgs") != None:
        parsed = parser.parse_args(import_["orgArgs"])
    else:
        parsed = import_["parsed"]
    v = import_.get("identityTypeInstance")
    if v != None:
        parser._registries["type"] = {v[0]: v[1]}
    return parser,parsed

