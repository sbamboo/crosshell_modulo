import pickle
import json

def has_tuple(obj):
    if isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, tuple):
                return True
    elif isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v, tuple) or isinstance(k, tuple):
                return True
    return False

def has_object_or_tuple(obj):
    if isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, (list, dict, int, float, str, bool, type(None))) == False:
                return True
    elif isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v, (list, dict, int, float, str, bool, type(None))) == False or isinstance(k, (list, dict, int, float, str, bool, type(None))) == False:
                return True
    return False

def serialize(obj, lossyTypes=False):
    """
    Function to serialize an object to text, takes:
    obj: <objectToSerialize>
    lossyTypes: If set to true the function will not return the datatype when returning json.
    """
    if lossyTypes == True:
        if isinstance(obj, (list, tuple, dict, int, float, str, bool, type(None))) and obj != 'pickle':
            return None, json.dumps(obj)
        else:
            return 'pickle', pickle.dumps(obj).hex()
    else:
        if isinstance(obj, (list, dict, int, float, str, bool, type(None))) and obj != 'pickle':
            if has_object_or_tuple(obj) == True:
                return 'pickle', pickle.dumps(obj).hex()    
            else:
                return type(obj).__name__, json.dumps(obj)
        else:
            return 'pickle', pickle.dumps(obj).hex()

def deserialize(type_, data, lossyTypes=False):
    """
    Function to deserialize an object from text, takes:
    type_: <typeOfObj>
    obj: <objectToSerialize>
    lossyTypes: If set to true the function will not care about the datatype when reading json.
    """
    if type_ == 'pickle':
        return pickle.loads(bytes.fromhex(data))
    else:
        if lossyTypes == True:
            return json.loads(data)
        else:
            if type_ in ('int', 'float', 'bool', 'NoneType'):
                return eval(data)
            elif type_ == 'str':
                return str(data)
            elif type_ == 'list':
                return json.loads(data)
            elif type_ == 'dict':
                return json.loads(data)
            elif type_ == 'tuple':
                return tuple(json.loads(data))
            
def _test(obj,lossyTypes=False):
    print(f"\033[90mST: \033[34m{obj}\033[0m")
    t,d = serialize(obj,lossyTypes)
    print(f"\033[90mTY: \033[31m{t}\033[0m\n\033[90mSER: \033[33m{d}\033[0m")
    print(f"\033[90mEN: \033[32m{deserialize(t,d,lossyTypes)}\033[0m")


# Works but is unefficient with large dictionaries not including tuples or dict still being represented as dicts, its data efficient but not size.