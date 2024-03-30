def expectedList(value) -> list:
    '''CSlib: Smal function for ensuring lists.'''
    if type(value) != list:
        return [value]
    else:
        return value

def picklePrioCopy(_dict):
    '''Function to deepcopy a dictionary of depth 1, it uses pickle when avaliable and if not for loops.'''
    try:
        import pickle
        return pickle.loads(pickle.dumps(_dict))
    except:
        nd = {}
        for sub in _dict:
            nd[sub] = _dict[sub].copy()
        return nd

def merge_dicts(dict1, obj):
    """
    Recursively merges dict2 into dict1 and returns the merged dictionary.
    """
    merged = dict1.copy()
    if type(obj) == dict:
        for key, value in obj.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # If both values are dictionaries, recursively merge them
                merged[key] = merge_dicts(merged[key], value)
            else:
                # Otherwise, update the value or add the key-value pair
                merged[key] = value
    elif type(obj) in [list,tuple]:
        merged.append(obj)
    else:
        merged = obj
    return merged

class exportableDict(dict):
    """Class for making dictionary .items()/.keys()/.items() exportable by casting their output to lists."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dictimplement_keys = self.keys
        self.__dictimplement_values = self.values
        self.keys = self.__exportable_keys
        """D.keys() -> a list object providing a view on D's keys"""
        self.values = self.__exportable_values
        """D.values() -> a list object providing a view on D's values"""
    def __exportable_keys(self) -> list:
        """D.__exportable_keys() -> a list object providing a view on D's keys"""
        return list(self.__dictimplement_keys())
    def __exportable_values(self) -> list:
        """D.__exportable_values() -> a list object providing a view on D's values"""
        return list(self.__dictimplement_values())
    def items(self) -> list:
        """D.items() -> a list object providing a view on D's items"""
        return list(zip(self.__dictimplement_keys(),self.__dictimplement_values()))