import os

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